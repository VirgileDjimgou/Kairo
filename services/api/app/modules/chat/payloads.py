from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.modules.chat.schemas import ChatCitationResponse
from app.modules.documents.models import Document, DocumentChunk


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: DocumentChunk
    document: Document
    score: float


@dataclass(frozen=True)
class StructuredContext:
    source_type: str
    title: str
    content: str


@dataclass(frozen=True)
class PreparedChatTurn:
    response_language: str
    conversation_id: UUID | None
    structured_contexts: list[StructuredContext]
    citations: list[ChatCitationResponse]
    source_types: list[str]
    system_prompt: str
    user_prompt: str
    confidence: float


def excerpt(text: str, limit: int = 220) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 1].rstrip()}..."


def build_citations(
    retrieved_chunks: list[RetrievedChunk],
    *,
    top_k: int,
) -> list[ChatCitationResponse]:
    return [
        ChatCitationResponse(
            chunk_id=item.chunk.id,
            document_id=item.document.id,
            document_version_id=item.chunk.document_version_id,
            document_title=item.document.title,
            excerpt=excerpt(item.chunk.text),
            score=item.score,
        )
        for item in retrieved_chunks[:top_k]
    ]


def collect_source_types(
    structured_contexts: list[StructuredContext],
    citations: list[ChatCitationResponse],
) -> list[str]:
    source_types = {context.source_type for context in structured_contexts}
    if citations:
        source_types.add("document")
    return sorted(source_types)


def render_structured_context(structured_contexts: list[StructuredContext]) -> str:
    if not structured_contexts:
        return ""
    return "\n\n".join(
        f"[{index}] {context.title}\n{context.content}"
        for index, context in enumerate(structured_contexts, start=1)
    )


def render_document_context(citations: list[ChatCitationResponse]) -> str:
    if not citations:
        return "No document sources were retrieved."
    return "\n\n".join(
        f"[{index}] {citation.document_title}: {citation.excerpt}"
        for index, citation in enumerate(citations, start=1)
    )


def compute_structured_confidence(structured_count: int, citation_count: int) -> float:
    confidence = 0.45 + (0.2 * structured_count) + (0.1 * citation_count)
    return min(1.0, confidence)


def serialize_citations(citations: list[ChatCitationResponse]) -> list[dict[str, object]]:
    return [
        {
            "chunk_id": str(citation.chunk_id),
            "document_id": str(citation.document_id),
            "document_version_id": str(citation.document_version_id),
            "document_title": citation.document_title,
            "excerpt": citation.excerpt,
            "score": citation.score,
        }
        for citation in citations
    ]
