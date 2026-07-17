from __future__ import annotations

import json
import re
from collections.abc import AsyncGenerator
from dataclasses import replace
from datetime import datetime, timezone
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.capabilities import (
    CAP_ANNOUNCEMENTS_WRITE,
    CAP_DISCIPLINARY_TENANT_READ,
    CAP_DISCIPLINARY_WRITE,
    CAP_DOCUMENTS_WRITE,
    CAP_EVENTS_SPORTS_WRITE,
    CAP_FINANCE_AUDIT,
    CAP_FINANCE_SELF_READ,
    CAP_FINANCE_TENANT_READ,
    CAP_POLICIES_WRITE,
    CAP_TENANT_ADMINISTRATION,
    capabilities_for_roles,
)
from app.core.config import settings
from app.core.privacy import preview_text
from app.modules.announcements.repository import AnnouncementRepository
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
    ChatMessageResponse,
    ChatQueryRequest,
    ChatQueryResponse,
)
from app.modules.contributions.service import ContributionService
from app.modules.disciplinary.repository import DisciplinaryRepository
from app.modules.documents.repository import DocumentRepository
from app.modules.events.models import Event
from app.modules.events.repository import EventRepository
from app.modules.membership.service import MembershipService
from app.modules.policies.service import PolicyService
from app.modules.rag.confidence import compute_confidence_score
from app.modules.rag.ranking import compute_keyword_overlap_ratio
from app.modules.rag.retrieval import build_access_policy
from app.providers.reranker.interface import RerankerProvider

logger = structlog.get_logger(__name__)

_PERSONAL_FINANCE_SELF_PATTERNS = (
    r"\bmy balance\b",
    r"\bmy dues\b",
    r"\bmy contribution(?:s)?\b",
    r"\bwhat do i owe\b",
    r"\bhow much do i owe\b",
    r"\bwhat is my balance\b",
    r"\bwhat is owing\b",
    r"\bmy statement\b",
    r"\b(mon|mes)\b.*\b(solde|cotisation(?:s)?|contribution(?:s)?|reste|paiement(?:s)?)\b",
    r"\bquelle est ma\b.*\b(cotisation|contribution)\b",
    r"\bquel est mon\b.*\b(solde|reste)\b",
    r"\b(mein|meine)\b.*\b(saldo|beitrag|beitraege|restbetrag|zahlung(?:en)?)\b",
    r"\bwie hoch ist mein\b.*\b(saldo|beitrag|restbetrag)\b",
)

_TENANT_FINANCE_PATTERNS = (
    r"\btenant summary\b",
    r"\bfinance summary\b",
    r"\bcontribution summary\b",
    r"\bcollection rate\b",
    r"\btotal balance\b",
    r"\btotal paid\b",
    r"\btotal expected\b",
    r"\boutstanding balance\b",
    r"\bfinance report\b",
    r"\bhow many contributions\b",
    r"\bhow many members have paid\b",
    r"\br[ée]sum[ée] financier\b",
    r"\bsynth[èe]se des cotisations\b",
    r"\btaux de recouvrement\b",
    r"\bsolde total\b",
    r"\btotal pay[ée]\b",
    r"\btotal attendu\b",
    r"\bzusammenfassung der finanzen\b",
    r"\bfinanz(?:en)?zusammenfassung\b",
    r"\beinziehungsquote\b",
    r"\bgesamtsaldo\b",
    r"\bgesamt bezahlt\b",
    r"\bgesamt erwartet\b",
)

_OTHER_MEMBER_FINANCE_PATTERNS = (
    r"\banother member\b.*\b(balance|dues|fee|fees|contribution|contributions|owed|owing)\b",
    r"\b(other|another|their|his|her)\b.*\b(balance|dues|fee|fees|contribution|contributions|owed|owing)\b",
    r"\b(balance|dues|fee|fees|contribution|contributions|owed|owing)\b.*\b(of|for)\b.*\b(member|user|profile)\b",
    r"\b(son|sa|ses|leur|leurs)\b.*\b(solde|cotisation(?:s)?|contribution(?:s)?|reste)\b",
    r"\b(solde|cotisation(?:s)?|contribution(?:s)?|reste)\b.*\b(d['e]|de|du|des|pour)\b.*\b(un autre membre|autre membre|membre|adh[ée]rent)\b",
    r"\b(solde|cotisation(?:s)?|contribution(?:s)?|reste)\b.*\b(d['e]|de|du|des|pour)\b\s+[a-zà-ÿ'-]+(?:\s+[a-zà-ÿ'-]+){1,2}\b",
    r"\b(sein|seine|seiner|ihre|ihr|deren)\b.*\b(saldo|beitrag|beitraege|restbetrag)\b",
    r"\b(saldo|beitrag|beitraege|restbetrag)\b.*\b(von|fuer|für)\b.*\b(einem anderen mitglied|anderen mitglied|mitglied)\b",
    r"\b(saldo|beitrag|beitraege|restbetrag)\b.*\b(von|fuer|für)\b\s+[a-zà-ÿ'-]+(?:\s+[a-zà-ÿ'-]+){1,2}\b",
)

_FINANCE_TOPIC_PATTERNS = (
    r"\bbalance\b",
    r"\bdues\b",
    r"\bfee(?:s)?\b",
    r"\bcontribution(?:s)?\b",
    r"\bowed\b",
    r"\bowing\b",
    r"\bsolde\b",
    r"\bcotisation(?:s)?\b",
    r"\breste\b",
    r"\bcontribution(?:s)?\b",
    r"\bsaldo\b",
    r"\bbeitrag\b",
    r"\bbeitraege\b",
    r"\brestbetrag\b",
)

_MESSAGES: dict[str, dict[str, str]] = {
    "other_member_finance_forbidden": {
        "fr": "Les demandes concernant les finances personnelles d'un autre membre ne sont pas autorisées.",
        "en": "Requests for another member's personal finance data are not allowed.",
        "de": "Anfragen zu den persoenlichen Finanzdaten eines anderen Mitglieds sind nicht erlaubt.",
    },
    "personal_finance_forbidden": {
        "fr": "Votre rôle ne peut pas accéder aux soldes personnels via le chat.",
        "en": "Your role cannot access personal contribution balances through chat.",
        "de": "Ihre Rolle darf persoenliche Beitragssalden nicht per Chat abrufen.",
    },
    "tenant_finance_forbidden": {
        "fr": "Votre rôle ne peut pas accéder aux synthèses financières globales via le chat.",
        "en": "Your role cannot access tenant-wide finance summaries through chat.",
        "de": "Ihre Rolle darf keine tenant-weiten Finanzzusammenfassungen per Chat abrufen.",
    },
    "no_authorized_answer": {
        "fr": "Je n'ai pas trouvé de réponse fiable dans les documents autorisés ni dans les données structurées auxquelles vous avez accès.",
        "en": "I could not find a reliable answer in the authorized documents or structured data available to you.",
        "de": "Ich konnte in den freigegebenen Dokumenten oder strukturierten Daten, auf die Sie zugreifen duerfen, keine verlaessliche Antwort finden.",
    },
    "no_authorized_source": {
        "fr": "Aucune source autorisée ne correspond à la question.",
        "en": "No authorized source matched the question.",
        "de": "Keine autorisierte Quelle passte zur Frage.",
    },
    "governance_forbidden": {
        "fr": "Votre rôle ne peut pas accéder aux synthèses de gouvernance via le chat.",
        "en": "Your role cannot access governance summaries through chat.",
        "de": "Ihre Rolle darf keine Governance-Zusammenfassungen per Chat abrufen.",
    },
    "publication_forbidden": {
        "fr": "Votre rôle ne peut pas accéder au contexte de publication via le chat.",
        "en": "Your role cannot access publication context through chat.",
        "de": "Ihre Rolle darf nicht auf den Publikationskontext per Chat zugreifen.",
    },
    "disciplinary_forbidden": {
        "fr": "Votre rôle ne peut pas accéder aux synthèses disciplinaires via le chat.",
        "en": "Your role cannot access disciplinary summaries through chat.",
        "de": "Ihre Rolle darf keine disziplinarischen Zusammenfassungen per Chat abrufen.",
    },
    "sports_forbidden": {
        "fr": "Votre rôle ne peut pas accéder au calendrier sportif via le chat.",
        "en": "Your role cannot access sports schedules through chat.",
        "de": "Ihre Rolle darf nicht auf Sportkalender per Chat zugreifen.",
    },
}

_GOVERNANCE_SUMMARY_PATTERNS = (
    r"\bgovernance summary\b",
    r"\borganization summary\b",
    r"\borganization overview\b",
    r"\btenant overview\b",
    r"\bexecutive overview\b",
    r"\bboard overview\b",
    r"\bmember directory overview\b",
    r"\bmember count\b",
    r"\bdocument count\b",
    r"\bannouncement count\b",
    r"\bevent count\b",
    r"\bpolicy count\b",
    r"\br[ée]sum[ée] de gouvernance\b",
    r"\baper[çc]u de l'organisation\b",
    r"\baper[çc]u du tenant\b",
    r"\bnombre de membres\b",
    r"\bgovernance-zusammenfassung\b",
    r"\bvereinsueberblick\b",
    r"\btenant-ueberblick\b",
    r"\banzahl der mitglieder\b",
)

_PUBLICATION_CONTEXT_PATTERNS = (
    r"\bpublication context\b",
    r"\bofficial publication\b",
    r"\bofficial publications\b",
    r"\bpublication status\b",
    r"\bannouncement status\b",
    r"\bwhat should i publish\b",
    r"\bwhat needs to be published\b",
    r"\bofficial notices\b",
    r"\bcontexte de publication\b",
    r"\bpublication officielle\b",
    r"\bquelles annonces sont actives\b",
    r"\bquels documents sont pr[êe]ts [àa] [êe]tre publi[ée]s\b",
    r"\bpublikationskontext\b",
    r"\boffizielle veroeffentlichung\b",
    r"\bwelche ankuendigungen sind aktiv\b",
    r"\bwelche dokumente sind zur veroeffentlichung bereit\b",
)

_DISCIPLINARY_SUMMARY_PATTERNS = (
    r"\bdisciplinary summary\b",
    r"\bsanctions overview\b",
    r"\bcompliance overview\b",
    r"\bopen cases\b",
    r"\bcase summary\b",
    r"\br[ée]sum[ée] disciplinaire\b",
    r"\baper[çc]u des sanctions\b",
    r"\bcombien de dossiers sont ouverts\b",
    r"\bdisziplinarische zusammenfassung\b",
    r"\bsanktionsuebersicht\b",
    r"\bwieviele faelle sind offen\b",
)

_SPORTS_SCHEDULE_PATTERNS = (
    r"\bsports schedule\b",
    r"\bsports calendar\b",
    r"\btraining schedule\b",
    r"\bfixture schedule\b",
    r"\bupcoming sports events\b",
    r"\bnext sports event\b",
    r"\bsports plan\b",
    r"\bcalendrier sportif\b",
    r"\bprochain [ée]v[ée]nement sportif\b",
    r"\bwelcher sportkalender\b",
    r"\bnaechste sportveranstaltung\b",
    r"\bsportkalender\b",
)



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
        self._membership_service = MembershipService(db)
        self._contribution_service = ContributionService(db)
        self._announcement_repo = AnnouncementRepository(db)
        self._disciplinary_repo = DisciplinaryRepository(db)
        self._event_repo = EventRepository(db)
        self._policy_service = PolicyService(db)
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
        if _question_mentions_any(normalized_question, _FINANCE_TOPIC_PATTERNS):
            return "finance"
        if _question_mentions_any(normalized_question, _GOVERNANCE_SUMMARY_PATTERNS):
            return "governance"
        if _question_mentions_any(normalized_question, _PUBLICATION_CONTEXT_PATTERNS):
            return "publication"
        if _question_mentions_any(normalized_question, _DISCIPLINARY_SUMMARY_PATTERNS):
            return "disciplinary"
        if _question_mentions_any(normalized_question, _SPORTS_SCHEDULE_PATTERNS):
            return "sports"
        return None

    async def _build_structured_contexts(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
        capabilities: tuple[str, ...],
        question: str,
        response_language: str,
    ) -> tuple[list[StructuredContext], str | None]:
        normalized = normalize_question(question)
        contexts: list[StructuredContext] = []

        if _question_mentions_other_member_finance(normalized):
            return [], _message("other_member_finance_forbidden", response_language)

        if _question_mentions_personal_finance(normalized):
            if CAP_FINANCE_SELF_READ not in capabilities:
                return [], _message("personal_finance_forbidden", response_language)
            balance = await self._membership_service.get_my_balance(tenant_id, user_id)
            contexts.append(
                StructuredContext(
                    source_type="structured:member_balance",
                    title="Personal contribution balance",
                    content=(
                        f"Member: {balance.profile.display_name} "
                        f"(code {balance.profile.member_code})\n"
                        f"Total expected: {balance.total_expected} EUR\n"
                        f"Total paid: {balance.total_paid} EUR\n"
                        f"Outstanding balance: {balance.total_balance} EUR\n"
                        f"Contribution records: {balance.contribution_count}"
                    ),
                )
            )

        if _question_mentions_tenant_finance(normalized):
            if not _can_view_tenant_finance(capabilities):
                return [], _message("tenant_finance_forbidden", response_language)
            summary = await self._contribution_service.get_summary(tenant_id)
            contexts.append(
                StructuredContext(
                    source_type="structured:finance_summary",
                    title="Tenant contribution summary",
                    content=(
                        f"Contribution records: {summary['total_count']}\n"
                        f"Total expected: {summary['total_expected']} EUR\n"
                        f"Total paid: {summary['total_paid']} EUR\n"
                        f"Outstanding balance: {summary['total_balance']} EUR"
                    ),
                )
            )

        governance_context, refusal = await self._build_governance_summary_context(
            tenant_id=tenant_id,
            capabilities=capabilities,
            normalized_question=normalized,
            response_language=response_language,
        )
        if refusal:
            return [], refusal
        if governance_context:
            contexts.append(governance_context)

        publication_context, refusal = await self._build_publication_context(
            tenant_id=tenant_id,
            capabilities=capabilities,
            normalized_question=normalized,
            response_language=response_language,
        )
        if refusal:
            return [], refusal
        if publication_context:
            contexts.append(publication_context)

        disciplinary_context, refusal = await self._build_disciplinary_summary_context(
            tenant_id=tenant_id,
            capabilities=capabilities,
            normalized_question=normalized,
            response_language=response_language,
        )
        if refusal:
            return [], refusal
        if disciplinary_context:
            contexts.append(disciplinary_context)

        sports_context, refusal = await self._build_sports_schedule_context(
            tenant_id=tenant_id,
            capabilities=capabilities,
            normalized_question=normalized,
            response_language=response_language,
        )
        if refusal:
            return [], refusal
        if sports_context:
            contexts.append(sports_context)

        return contexts, None

    async def _build_governance_summary_context(
        self,
        *,
        tenant_id: UUID,
        capabilities: tuple[str, ...],
        normalized_question: str,
        response_language: str,
    ) -> tuple[StructuredContext | None, str | None]:
        if not _question_mentions_any(normalized_question, _GOVERNANCE_SUMMARY_PATTERNS):
            return None, None
        if not _can_view_governance_summary(capabilities):
            return None, _message("governance_forbidden", response_language)

        documents = await self._repo.list_documents(tenant_id)
        members = await self._membership_service.list_profiles(tenant_id)
        policies = await self._policy_service.list_public(tenant_id)
        announcements = await self._announcement_repo.list_visible_active_by_tenant(tenant_id)
        events = await self._event_repo.list_visible_by_tenant(tenant_id)
        upcoming_events = [event for event in events if _is_future_datetime(event.start_at)]
        summary_lines = [
            f"Members in tenant: {len(members)}",
            f"Documents available: {len(documents)}",
            f"Published policies: {len(policies)}",
            f"Active announcements: {len(announcements)}",
            f"Upcoming events: {len(upcoming_events)}",
        ]
        if policies:
            summary_lines.append("Recent policies:")
            summary_lines.extend(
                f"- {policy.title} ({policy.status})" for policy in policies[:3]
            )
        if announcements:
            summary_lines.append("Recent announcements:")
            summary_lines.extend(
                f"- {announcement.title} ({_format_datetime(announcement.published_at)})"
                for announcement in announcements[:3]
            )

        return (
            StructuredContext(
                source_type="structured:governance_summary",
                title="Tenant governance summary",
                content="\n".join(summary_lines),
            ),
            None,
        )

    async def _build_publication_context(
        self,
        *,
        tenant_id: UUID,
        capabilities: tuple[str, ...],
        normalized_question: str,
        response_language: str,
    ) -> tuple[StructuredContext | None, str | None]:
        if not _question_mentions_any(normalized_question, _PUBLICATION_CONTEXT_PATTERNS):
            return None, None
        if not _can_view_publication_context(capabilities):
            return None, _message("publication_forbidden", response_language)

        policies = await self._policy_service.list_all(tenant_id)
        announcements = await self._announcement_repo.list_visible_active_by_tenant(tenant_id)
        policy_counts = {"published": 0, "draft": 0, "archived": 0}
        for policy in policies:
            policy_counts[policy.status] = policy_counts.get(policy.status, 0) + 1

        summary_lines = [
            f"Policies in workspace: {len(policies)}",
            f"Published policies: {policy_counts['published']}",
            f"Draft policies: {policy_counts['draft']}",
            f"Archived policies: {policy_counts['archived']}",
            f"Active announcements: {len(announcements)}",
        ]
        if announcements:
            summary_lines.append("Recent active announcements:")
            summary_lines.extend(
                f"- {announcement.title} ({_format_datetime(announcement.published_at)})"
                for announcement in announcements[:3]
            )
        if policies:
            summary_lines.append("Recent policies:")
            summary_lines.extend(
                f"- {policy.title} ({policy.status})" for policy in policies[:3]
            )

        return (
            StructuredContext(
                source_type="structured:publication_context",
                title="Official publication context",
                content="\n".join(summary_lines),
            ),
            None,
        )

    async def _build_disciplinary_summary_context(
        self,
        *,
        tenant_id: UUID,
        capabilities: tuple[str, ...],
        normalized_question: str,
        response_language: str,
    ) -> tuple[StructuredContext | None, str | None]:
        if not _question_mentions_any(normalized_question, _DISCIPLINARY_SUMMARY_PATTERNS):
            return None, None
        if not _can_view_disciplinary_summary(capabilities):
            return None, _message("disciplinary_forbidden", response_language)

        records = await self._disciplinary_repo.list_by_tenant(tenant_id)
        status_counts = {"open": 0, "under_review": 0, "resolved": 0, "waived": 0}
        for record in records:
            status_counts[record.status] = status_counts.get(record.status, 0) + 1

        summary_lines = [
            f"Disciplinary cases: {len(records)}",
            f"Open cases: {status_counts['open']}",
            f"Under review: {status_counts['under_review']}",
            f"Resolved: {status_counts['resolved']}",
            f"Waived: {status_counts['waived']}",
        ]

        return (
            StructuredContext(
                source_type="structured:disciplinary_summary",
                title="Disciplinary summary",
                content="\n".join(summary_lines),
            ),
            None,
        )

    async def _build_sports_schedule_context(
        self,
        *,
        tenant_id: UUID,
        capabilities: tuple[str, ...],
        normalized_question: str,
        response_language: str,
    ) -> tuple[StructuredContext | None, str | None]:
        if not _question_mentions_any(normalized_question, _SPORTS_SCHEDULE_PATTERNS):
            return None, None
        if not _can_view_sports_schedule(capabilities):
            return None, _message("sports_forbidden", response_language)

        events = await self._event_repo.list_by_tenant(tenant_id)
        sports_events = [event for event in events if self._is_sports_event(event)]
        upcoming_events = [
            event
            for event in sports_events
            if event.status == "published" and _is_future_datetime(event.start_at)
        ]
        summary_lines = [
            f"Sports events in tenant: {len(sports_events)}",
            f"Upcoming sports events: {len(upcoming_events)}",
        ]
        if upcoming_events:
            summary_lines.append("Next sports events:")
            summary_lines.extend(
                (
                    f"- {event.title} ({_format_datetime(event.start_at)})"
                    + (f" at {event.location}" if event.location else "")
                )
                for event in upcoming_events[:3]
            )

        return (
            StructuredContext(
                source_type="structured:sports_schedule",
                title="Sports schedule",
                content="\n".join(summary_lines),
            ),
            None,
        )

    def _parse_metadata(self, value: str | dict | None) -> dict[str, object]:
        if value in (None, ""):
            return {}
        if isinstance(value, dict):
            return dict(value)
        if not isinstance(value, str):
            return {}
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _is_sports_event(self, event: Event) -> bool:
        metadata = self._parse_metadata(event.metadata_json)
        return metadata.get("workspace") == "sports"

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
        structured_contexts, policy_refusal = await self._build_structured_contexts(
            tenant_id=tenant_id,
            user_id=user_id,
            capabilities=capabilities,
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
                answer=_message("no_authorized_answer", response_language),
                citations=[],
                source_types=[],
                confidence=0.0,
                refused=True,
                refusal_reason=_message("no_authorized_source", response_language),
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
        for message in history:
            role_label = "User" if message.role == "user" else "Assistant"
            history_lines.append(f"{role_label}: {message.content[:500]}")
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
            yield f"data: {json.dumps({'type': 'error', 'content': refusal_response.answer})}\n\n"
            return
        assert prepared_turn is not None

        full_answer_parts: list[str] = []
        yield f"data: {json.dumps({'type': 'start', 'conversation_id': str(prepared_turn.conversation_id) if prepared_turn.conversation_id else None})}\n\n"

        async for token in self._llm.generate_stream(
            system_prompt=prepared_turn.system_prompt,
            user_prompt=prepared_turn.user_prompt,
            max_tokens=settings.llm_max_tokens,
        ):
            full_answer_parts.append(token)
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

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
def _question_mentions_personal_finance(question: str) -> bool:
    return any(re.search(pattern, question) for pattern in _PERSONAL_FINANCE_SELF_PATTERNS)


def _question_mentions_tenant_finance(question: str) -> bool:
    return any(re.search(pattern, question) for pattern in _TENANT_FINANCE_PATTERNS)


def _question_mentions_other_member_finance(question: str) -> bool:
    if any(re.search(pattern, question) for pattern in _OTHER_MEMBER_FINANCE_PATTERNS):
        return True
    return (
        _question_mentions_finance_topic(question)
        and not _question_mentions_personal_finance(question)
        and not _question_mentions_tenant_finance(question)
        and _question_mentions_named_target(question)
    )


def _question_mentions_finance_topic(question: str) -> bool:
    return any(re.search(pattern, question) for pattern in _FINANCE_TOPIC_PATTERNS)


def _question_mentions_named_target(question: str) -> bool:
    return any(
        re.search(pattern, question)
        for pattern in (
            r"\b(of|for|de|du|des|pour|von|fuer|für)\b\s+[a-zà-ÿ'-]+(?:\s+[a-zà-ÿ'-]+){1,2}\b",
            r"\b(other|another|their|his|her|son|sa|ses|leur|leurs|sein|seine|ihr|ihre)\b",
        )
    )


def _can_view_tenant_finance(capabilities: tuple[str, ...]) -> bool:
    return any(
        capability in capabilities
        for capability in (
            CAP_FINANCE_TENANT_READ,
            CAP_FINANCE_AUDIT,
            CAP_TENANT_ADMINISTRATION,
        )
    )


def _question_mentions_any(question: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, question) for pattern in patterns)


def _message(key: str, language: str) -> str:
    translations = _MESSAGES[key]
    return translations.get(language, translations["en"])


def _can_view_governance_summary(capabilities: tuple[str, ...]) -> bool:
    return any(
        capability in capabilities
        for capability in (
            CAP_FINANCE_TENANT_READ,
            CAP_FINANCE_AUDIT,
            CAP_TENANT_ADMINISTRATION,
        )
    )


def _can_view_publication_context(capabilities: tuple[str, ...]) -> bool:
    return any(
        capability in capabilities
        for capability in (
            CAP_DOCUMENTS_WRITE,
            CAP_POLICIES_WRITE,
            CAP_ANNOUNCEMENTS_WRITE,
            CAP_TENANT_ADMINISTRATION,
        )
    )


def _can_view_disciplinary_summary(capabilities: tuple[str, ...]) -> bool:
    return any(
        capability in capabilities
        for capability in (
            CAP_DISCIPLINARY_TENANT_READ,
            CAP_DISCIPLINARY_WRITE,
            CAP_TENANT_ADMINISTRATION,
        )
    )


def _can_view_sports_schedule(capabilities: tuple[str, ...]) -> bool:
    return any(
        capability in capabilities
        for capability in (
            CAP_EVENTS_SPORTS_WRITE,
            CAP_TENANT_ADMINISTRATION,
        )
    )


def _format_datetime(value: datetime | None) -> str:
    if value is None:
        return "unknown date"
    if value.tzinfo is None:
        normalized = value.replace(tzinfo=timezone.utc)
    else:
        normalized = value.astimezone(timezone.utc)
    return normalized.strftime("%Y-%m-%d %H:%M UTC")


def _is_future_datetime(value: datetime | None) -> bool:
    if value is None:
        return False
    if value.tzinfo is None:
        normalized = value.replace(tzinfo=timezone.utc)
    else:
        normalized = value.astimezone(timezone.utc)
    return normalized >= datetime.now(timezone.utc)


def _excerpt(text: str, limit: int = 220) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 1].rstrip()}…"
