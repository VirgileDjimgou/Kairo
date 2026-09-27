from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from dataclasses import replace
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.capabilities import capabilities_for_roles
from app.core.config import settings
from app.core.privacy import preview_text
from app.modules.chat.contexts.contracts import ContextRequest
from app.modules.chat.contexts.messages import message
from app.modules.chat.contexts.patterns import (
    DISCIPLINARY_SUMMARY_PATTERNS,
    FINANCE_TOPIC_PATTERNS,
    GOVERNANCE_SUMMARY_PATTERNS,
    PUBLICATION_CONTEXT_PATTERNS,
    SPORTS_SCHEDULE_PATTERNS,
    question_mentions_any,
    question_mentions_other_member_finance,
)
from app.modules.chat.contexts.registry import build_default_registry
from app.modules.chat.domain_policy import ChatDomainPolicy, build_chat_domain_policy
from app.modules.chat.models import ChatQueryLog
from app.modules.chat.payloads import (
    PreparedChatTurn,
    RetrievedChunk,
    StructuredContext,
    build_citations,
    collect_source_types,
    compute_structured_confidence,
    render_document_context,
    render_structured_context,
    serialize_citations,
)
from app.modules.chat.prompting import (
    build_prompt_context,
    build_retrieval_query,
    normalize_question,
    primary_role,
)
from app.modules.chat.repository import ChatRepository
from app.modules.chat.schemas import (
    ChatCitationResponse,
    ChatConversationDetailResponse,
    ChatConversationResponse,
    ChatDomainPolicyResponse,
    ChatMessageResponse,
    ChatQueryRequest,
    ChatQueryResponse,
)
from app.modules.documents.repository import DocumentRepository
from app.modules.rag.confidence import compute_confidence_score
from app.modules.rag.ranking import compute_keyword_overlap_ratio
from app.modules.rag.retrieval import build_access_policy
from app.modules.tenancy.repository import TenancyRepository
from app.providers.ai_runtime.remote import AiRuntimeUnavailableError
from app.providers.reranker.interface import RerankerProvider

logger = structlog.get_logger(__name__)

class ChatService:
    def __init__(
        self,
        db: AsyncSession,
        *,
        embedding_provider=None,
        vector_store_provider=None,
        llm_provider=None,
        reranker_provider: RerankerProvider | None = None,
    ) -> None:
        self._db = db
        self._chat_repo = ChatRepository(db)
        self._repo = DocumentRepository(db)
        self._context_registry = build_default_registry(db)
        self._tenancy_repo = TenancyRepository(db)
        self._embedding = embedding_provider
        self._vector_store = vector_store_provider
        self._llm = llm_provider
        self._reranker = reranker_provider

    async def query(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
        roles: list[str],
        request: ChatQueryRequest,
    ) -> ChatQueryResponse:
        prepared_turn, refusal_response = await self._prepare_chat_turn(
            tenant_id=tenant_id,
            user_id=user_id,
            roles=roles,
            request=request,
        )
        if refusal_response is not None:
            await self._log_query(
                tenant_id=tenant_id,
                user_id=user_id,
                request=request,
                response=refusal_response,
            )
            return refusal_response
        assert prepared_turn is not None

        answer = await self._llm.generate(
            system_prompt=prepared_turn.system_prompt,
            user_prompt=prepared_turn.user_prompt,
            max_tokens=settings.llm_max_tokens,
        )

        response = ChatQueryResponse(
            answer=answer.strip(),
            conversation_id=prepared_turn.conversation_id,
            citations=prepared_turn.citations,
            source_types=prepared_turn.source_types,
            confidence=prepared_turn.confidence,
            refused=False,
        )

        response.conversation_id = await self._persist_conversation_turn(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=prepared_turn.conversation_id,
            question=request.question,
            answer=response.answer,
            citations=prepared_turn.citations,
        )

        await self._log_query(
            tenant_id=tenant_id,
            user_id=user_id,
            request=request,
            response=response,
        )
        return response

    async def get_domain_policy(
        self,
        *,
        tenant_id: UUID,
        roles: list[str],
    ) -> ChatDomainPolicyResponse:
        policy = await self._resolve_chat_domain_policy(
            tenant_id=tenant_id,
            capabilities=capabilities_for_roles(roles),
        )
        return ChatDomainPolicyResponse(allowed_domains=policy.allowed_domains())

    # --- Conversation CRUD ---

    async def list_conversations(
        self, *, tenant_id: UUID, user_id: UUID
    ) -> list[ChatConversationResponse]:
        conversations = await self._chat_repo.list_conversations(
            tenant_id=tenant_id, user_id=user_id
        )
        result: list[ChatConversationResponse] = []
        for conv in conversations:
            messages = await self._chat_repo.get_messages_for_conversation(
                conversation_id=conv.id, limit=1
            )
            message_count = await self._chat_repo.count_messages_for_conversation(
                conversation_id=conv.id
            )
            last_msg = messages[-1] if messages else None
            result.append(
                ChatConversationResponse(
                    id=conv.id,
                    tenant_id=conv.tenant_id,
                    user_id=conv.user_id,
                    title=conv.title,
                    message_count=message_count,
                    last_message_preview=preview_text(last_msg.content, max_length=100) if last_msg else None,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                )
            )
        return result

    async def create_conversation(
        self, *, tenant_id: UUID, user_id: UUID, title: str
    ) -> ChatConversationResponse:
        conv = await self._chat_repo.create_conversation(
            tenant_id=tenant_id, user_id=user_id, title=title
        )
        return ChatConversationResponse(
            id=conv.id,
            tenant_id=conv.tenant_id,
            user_id=conv.user_id,
            title=conv.title,
            message_count=0,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )

    async def get_conversation(
        self, *, conversation_id: UUID, tenant_id: UUID, user_id: UUID
    ) -> ChatConversationDetailResponse | None:
        conv = await self._chat_repo.get_conversation(
            conversation_id=conversation_id, tenant_id=tenant_id, user_id=user_id
        )
        if conv is None:
            return None
        return ChatConversationDetailResponse(
            id=conv.id,
            tenant_id=conv.tenant_id,
            user_id=conv.user_id,
            title=conv.title,
            messages=[
                ChatMessageResponse(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    citations_json=json.loads(msg.citations_json) if msg.citations_json else [],
                    created_at=msg.created_at,
                )
                for msg in conv.messages
            ],
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )

    async def update_conversation(
        self, *, conversation_id: UUID, tenant_id: UUID, user_id: UUID, title: str
    ) -> ChatConversationResponse | None:
        conv = await self._chat_repo.get_conversation(
            conversation_id=conversation_id, tenant_id=tenant_id, user_id=user_id
        )
        if conv is None:
            return None
        await self._chat_repo.update_conversation_title(
            conversation_id=conversation_id, title=title
        )
        await self._db.flush()
        message_count = await self._chat_repo.count_messages_for_conversation(conversation_id=conversation_id)
        return ChatConversationResponse(
            id=conv.id,
            tenant_id=conv.tenant_id,
            user_id=conv.user_id,
            title=title,
            message_count=message_count,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )

    async def delete_conversation(
        self, *, conversation_id: UUID, tenant_id: UUID, user_id: UUID
    ) -> bool:
        return await self._chat_repo.delete_conversation(
            conversation_id=conversation_id, tenant_id=tenant_id, user_id=user_id
        )

    # --- Existing helpers (unchanged) ---

    def _normalize_response_language(self, language: str | None) -> str:
        normalized = (language or "fr").strip().lower()
        if normalized in {"fr", "en", "de"}:
            return normalized
        return "fr"

    def _detect_retrieval_topic(self, normalized_question: str) -> str | None:
        if question_mentions_any(normalized_question, FINANCE_TOPIC_PATTERNS):
            return "finance"
        if question_mentions_any(normalized_question, GOVERNANCE_SUMMARY_PATTERNS):
            return "governance"
        if question_mentions_any(normalized_question, PUBLICATION_CONTEXT_PATTERNS):
            return "publication"
        if question_mentions_any(normalized_question, DISCIPLINARY_SUMMARY_PATTERNS):
            return "disciplinary"
        if question_mentions_any(normalized_question, SPORTS_SCHEDULE_PATTERNS):
            return "sports"
        return None

    async def _build_structured_contexts(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
        capabilities: tuple[str, ...],
        domain_policy: ChatDomainPolicy,
        question: str,
        response_language: str,
    ) -> tuple[list[StructuredContext], str | None]:
        normalized = normalize_question(question)

        if question_mentions_other_member_finance(normalized):
            return [], message("other_member_finance_forbidden", response_language)

        request = ContextRequest(
            tenant_id=tenant_id,
            user_id=user_id,
            capabilities=capabilities,
            question=question,
            normalized_question=normalized,
            response_language=response_language,
            domain_policy=domain_policy,
        )
        return await self._context_registry.collect_all(request)

    def _prioritize_retrieved_chunks(
        self,
        retrieved_chunks: list[RetrievedChunk],
        *,
        response_language: str,
    ) -> list[RetrievedChunk]:
        if not retrieved_chunks:
            return []

        same_language: list[RetrievedChunk] = []
        fallback: list[RetrievedChunk] = []
        for item in retrieved_chunks:
            document_language = (item.document.language or "").strip().lower()
            if document_language == response_language:
                same_language.append(item)
            else:
                fallback.append(item)

        def weighted_score(item: RetrievedChunk) -> float:
            document_language = (item.document.language or "").strip().lower()
            boost = settings.rag_language_boost if document_language == response_language else 0.0
            return item.score + boost

        prioritized = sorted(same_language, key=weighted_score, reverse=True)
        prioritized.extend(sorted(fallback, key=weighted_score, reverse=True))
        return prioritized

    def _apply_keyword_rank_boost(
        self,
        retrieved_chunks: list[RetrievedChunk],
        *,
        question: str,
    ) -> list[RetrievedChunk]:
        if not retrieved_chunks or settings.rag_keyword_match_boost <= 0:
            return retrieved_chunks

        boosted_chunks: list[RetrievedChunk] = []
        for item in retrieved_chunks:
            rank_content = f"{item.document.title}\n{item.chunk.text}"
            overlap_ratio = compute_keyword_overlap_ratio(
                query=question,
                content=rank_content,
            )
            boosted_chunks.append(
                replace(
                    item,
                    score=item.score + (overlap_ratio * settings.rag_keyword_match_boost),
                )
            )
        return boosted_chunks

    def _log_retrieval_summary(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
        role_code: str,
        response_language: str,
        retrieval_mode: str,
        requested_top_k: int,
        candidate_count: int,
        authorized_count: int,
        returned_count: int,
    ) -> None:
        logger.info(
            "chat_retrieval_summary",
            tenant_id=str(tenant_id),
            user_id=str(user_id),
            role_code=role_code,
            response_language=response_language,
            retrieval_mode=retrieval_mode,
            requested_top_k=requested_top_k,
            candidate_count=candidate_count,
            authorized_count=authorized_count,
            returned_count=returned_count,
            rerank_enabled=settings.rag_rerank_enabled and self._reranker is not None,
            language_boost=settings.rag_language_boost,
            keyword_match_boost=settings.rag_keyword_match_boost,
            score_threshold=settings.rag_score_threshold,
        )

    async def _load_and_filter_results(
        self,
        policy,
        qdrant_results: list[dict],
    ) -> list[RetrievedChunk]:
        chunk_ids = [
            UUID(str(result["payload"]["chunk_id"]))
            for result in qdrant_results
            if result.get("payload", {}).get("chunk_id")
        ]
        if not chunk_ids:
            return []

        rows = await self._repo.get_chunks_with_documents(policy.tenant_id, chunk_ids)
        chunks_by_id = {chunk.id: (chunk, document) for chunk, document in rows}

        matched: list[RetrievedChunk] = []
        for result in qdrant_results:
            payload = result.get("payload") or {}
            chunk_id_raw = payload.get("chunk_id")
            if not chunk_id_raw:
                continue
            item = chunks_by_id.get(UUID(str(chunk_id_raw)))
            if item is None:
                continue
            chunk, document = item
            if not policy.can_access(document):
                continue
            matched.append(
                RetrievedChunk(
                    chunk=chunk,
                    document=document,
                    score=float(result.get("score", 0.0)),
                )
            )
        return matched

    async def _prepare_chat_turn(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
        roles: list[str],
        request: ChatQueryRequest,
    ) -> tuple[PreparedChatTurn | None, ChatQueryResponse | None]:
        capabilities = capabilities_for_roles(roles)
        response_language = self._normalize_response_language(request.response_language)
        domain_policy = await self._resolve_chat_domain_policy(
            tenant_id=tenant_id,
            capabilities=capabilities,
        )
        structured_contexts, policy_refusal = await self._build_structured_contexts(
            tenant_id=tenant_id,
            user_id=user_id,
            capabilities=capabilities,
            domain_policy=domain_policy,
            question=request.question,
            response_language=response_language,
        )
        if policy_refusal:
            return None, ChatQueryResponse(
                answer=policy_refusal,
                citations=[],
                source_types=["policy:structured_redaction"],
                confidence=1.0,
                refused=True,
                refusal_reason=policy_refusal,
            )

        history_block = await self._build_history_block(request.conversation_id)
        citations = await self._retrieve_citations(
            tenant_id=tenant_id,
            user_id=user_id,
            roles=roles,
            question=request.question,
            response_language=response_language,
            top_k=request.top_k,
        )
        if not citations and not structured_contexts:
            return None, ChatQueryResponse(
                answer=message("no_authorized_answer", response_language),
                citations=[],
                source_types=[],
                confidence=0.0,
                refused=True,
                refusal_reason=message("no_authorized_source", response_language),
            )

        source_types = collect_source_types(structured_contexts, citations)
        prompt_package = build_prompt_context(
            question=request.question,
            response_language=response_language,
            primary_role_code=primary_role(roles),
            structured_block=render_structured_context(structured_contexts),
            document_block=render_document_context(citations),
            history_block=history_block,
        )
        confidence = max(
            compute_confidence_score(
                [{"score": citation.score} for citation in citations],
                rerank_enabled=self._reranker is not None,
            ),
            compute_structured_confidence(len(structured_contexts), len(citations)),
        )
        return (
            PreparedChatTurn(
                response_language=response_language,
                conversation_id=request.conversation_id,
                structured_contexts=structured_contexts,
                citations=citations,
                source_types=source_types,
                system_prompt=prompt_package.system_prompt,
                user_prompt=prompt_package.user_prompt,
                confidence=confidence,
            ),
            None,
        )

    async def _resolve_chat_domain_policy(
        self,
        *,
        tenant_id: UUID,
        capabilities: tuple[str, ...],
    ) -> ChatDomainPolicy:
        tenant = await self._tenancy_repo.get_tenant_by_id(tenant_id)
        tenant_settings = tenant.settings_json if tenant else None
        return build_chat_domain_policy(
            capabilities=capabilities,
            tenant_settings_json=tenant_settings,
        )

    async def _build_history_block(self, conversation_id: UUID | None) -> str:
        if conversation_id is None:
            return ""

        history = await self._chat_repo.get_messages_for_conversation(
            conversation_id=conversation_id,
            limit=settings.conversation_max_history,
        )
        if not history:
            return ""

        history_lines = []
        for history_message in history:
            role_label = "User" if history_message.role == "user" else "Assistant"
            history_lines.append(f"{role_label}: {history_message.content[:500]}")
        return "\n".join(history_lines)

    async def _retrieve_citations(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
        roles: list[str],
        question: str,
        response_language: str,
        top_k: int,
    ) -> list[ChatCitationResponse]:
        normalized_question = normalize_question(question)
        role_code = primary_role(roles)
        retrieval_query = build_retrieval_query(
            normalized_question=normalized_question,
            response_language=response_language,
            primary_role_code=role_code,
            topic=self._detect_retrieval_topic(normalized_question),
        )
        policy = build_access_policy(tenant_id=tenant_id, user_id=user_id, roles=roles)
        query_vector = await self._embedding.embed_texts([retrieval_query])
        qdrant_results = self._vector_store.search_chunk_vectors(
            tenant_id=tenant_id,
            query_vector=query_vector[0],
            query_text=retrieval_query,
            limit=max(top_k, settings.rag_top_k) * settings.rag_candidate_multiplier,
            score_threshold=settings.rag_score_threshold,
            hybrid=settings.rag_hybrid_search,
        )
        retrieval_mode = str(qdrant_results[0].get("retrieval_mode", "dense")) if qdrant_results else "dense"
        retrieved_chunks = await self._load_and_filter_results(policy, qdrant_results)
        authorized_count = len(retrieved_chunks)
        retrieved_chunks = self._apply_keyword_rank_boost(
            retrieved_chunks,
            question=question,
        )
        retrieved_chunks = self._prioritize_retrieved_chunks(
            retrieved_chunks,
            response_language=response_language,
        )
        retrieved_chunks = self._rerank_retrieved_chunks(
            retrieved_chunks,
            question=question,
            top_k=top_k,
        )
        self._log_retrieval_summary(
            tenant_id=tenant_id,
            user_id=user_id,
            role_code=role_code,
            response_language=response_language,
            retrieval_mode=retrieval_mode,
            requested_top_k=top_k,
            candidate_count=len(qdrant_results),
            authorized_count=authorized_count,
            returned_count=min(len(retrieved_chunks), top_k),
        )
        return build_citations(retrieved_chunks, top_k=top_k)

    def _rerank_retrieved_chunks(
        self,
        retrieved_chunks: list[RetrievedChunk],
        *,
        question: str,
        top_k: int,
    ) -> list[RetrievedChunk]:
        if not (settings.rag_rerank_enabled and self._reranker is not None and retrieved_chunks):
            return retrieved_chunks

        chunk_dicts = [
            {
                "id": str(item.chunk.id),
                "score": item.score,
                "payload": {"content": item.chunk.text},
            }
            for item in retrieved_chunks
        ]
        reranked = self._reranker.rerank(
            query=question,
            chunks=chunk_dicts,
            top_k=min(top_k, settings.rag_rerank_top_k),
        )
        reranked_ids = {item["id"] for item in reranked}
        filtered_chunks = [
            item for item in retrieved_chunks if str(item.chunk.id) in reranked_ids
        ]
        filtered_chunks.sort(
            key=lambda item: next(
                (entry["score"] for entry in reranked if entry["id"] == str(item.chunk.id)),
                0.0,
            ),
            reverse=True,
        )
        return filtered_chunks

    async def _persist_conversation_turn(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
        conversation_id: UUID | None,
        question: str,
        answer: str,
        citations: list[ChatCitationResponse],
    ) -> UUID:
        if conversation_id is None:
            conversation = await self._chat_repo.create_conversation(
                tenant_id=tenant_id,
                user_id=user_id,
                title=question[:80],
            )
            conversation_id = conversation.id

        citations_json = json.dumps(serialize_citations(citations), default=str)
        await self._chat_repo.add_message(
            conversation_id=conversation_id,
            role="user",
            content=question,
        )
        await self._chat_repo.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
            citations_json=citations_json,
        )
        await self._chat_repo.update_conversation_timestamp(conversation_id=conversation_id)
        return conversation_id

    async def query_stream(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
        roles: list[str],
        request: ChatQueryRequest,
    ) -> AsyncGenerator[str, None]:
        """Stream the answer token-by-token via SSE, persist on completion."""
        try:
            prepared_turn, refusal_response = await self._prepare_chat_turn(
                tenant_id=tenant_id,
                user_id=user_id,
                roles=roles,
                request=request,
            )
        except AiRuntimeUnavailableError:
            yield f"data: {json.dumps({'type': 'error', 'content': 'Assistant IA temporairement indisponible'})}\n\n"
            return
        if refusal_response is not None:
            await self._log_query(
                tenant_id=tenant_id,
                user_id=user_id,
                request=request,
                response=refusal_response,
            )
            yield f"data: {json.dumps({'type': 'error', 'content': refusal_response.answer})}\n\n"
            return
        assert prepared_turn is not None

        full_answer_parts: list[str] = []
        yield f"data: {json.dumps({'type': 'start', 'conversation_id': str(prepared_turn.conversation_id) if prepared_turn.conversation_id else None})}\n\n"

        try:
            async for token in self._llm.generate_stream(
                system_prompt=prepared_turn.system_prompt,
                user_prompt=prepared_turn.user_prompt,
                max_tokens=settings.llm_max_tokens,
            ):
                full_answer_parts.append(token)
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        except AiRuntimeUnavailableError:
            yield f"data: {json.dumps({'type': 'error', 'content': 'Assistant IA temporairement indisponible'})}\n\n"
            return

        full_answer = "".join(full_answer_parts).strip()
        conversation_id = await self._persist_conversation_turn(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=prepared_turn.conversation_id,
            question=request.question,
            answer=full_answer,
            citations=prepared_turn.citations,
        )

        # Build final response
        response = ChatQueryResponse(
            answer=full_answer,
            conversation_id=conversation_id,
            citations=prepared_turn.citations,
            source_types=prepared_turn.source_types,
            confidence=prepared_turn.confidence,
            refused=False,
        )
        await self._log_query(
            tenant_id=tenant_id,
            user_id=user_id,
            request=request,
            response=response,
        )

        yield f"data: {json.dumps({'type': 'done', 'conversation_id': str(conversation_id), 'confidence': prepared_turn.confidence, 'citations': serialize_citations(prepared_turn.citations), 'source_types': prepared_turn.source_types})}\n\n"

    async def _log_query(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
        request: ChatQueryRequest,
        response: ChatQueryResponse,
    ) -> None:
        log = ChatQueryLog(
            tenant_id=tenant_id,
            user_id=user_id,
            question=preview_text(request.question, max_length=240),
            answer=preview_text(response.answer, max_length=240),
            refused=response.refused,
            refusal_reason=(
                preview_text(response.refusal_reason, max_length=240)
                if response.refusal_reason
                else None
            ),
            confidence=response.confidence,
            citations_json=json.dumps(
                [
                    {
                        "chunk_id": citation.chunk_id,
                        "document_id": citation.document_id,
                        "document_version_id": citation.document_version_id,
                        "score": citation.score,
                    }
                    for citation in response.citations
                ],
                default=str,
            ),
            source_types_json=json.dumps(response.source_types),
        )
        self._db.add(log)
        await self._db.commit()
def _excerpt(text: str, limit: int = 220) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 1].rstrip()}â€¦"
