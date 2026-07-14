from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.config import settings


class ChatQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: UUID | None = None
    top_k: int = Field(default=settings.rag_top_k, ge=1, le=10)
    response_language: str = Field(default="fr", min_length=2, max_length=10)


class ChatCitationResponse(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_version_id: UUID
    document_title: str
    excerpt: str
    score: float


class ChatQueryResponse(BaseModel):
    answer: str
    conversation_id: UUID | None = None
    citations: list[ChatCitationResponse] = Field(default_factory=list)
    source_types: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    refused: bool = False
    refusal_reason: str | None = None


class ChatQueryLogResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    user_id: UUID
    question_preview: str
    answer_preview: str
    refused: bool
    refusal_reason_preview: str | None
    confidence: float
    citation_count: int
    source_types: list[str] = Field(default_factory=list)
    created_at: datetime


# --- Conversation Schemas ---


class ChatConversationCreate(BaseModel):
    title: str = Field(default="Nouvelle conversation", max_length=255)


class ChatConversationUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ChatMessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    citations_json: list[dict] = Field(default_factory=list)
    created_at: datetime


class ChatConversationResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    user_id: UUID
    title: str
    message_count: int = 0
    last_message_preview: str | None = None
    created_at: datetime
    updated_at: datetime


class ChatConversationDetailResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    user_id: UUID
    title: str
    messages: list[ChatMessageResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
