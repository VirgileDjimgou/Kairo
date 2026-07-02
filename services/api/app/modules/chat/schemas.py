from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=4, ge=1, le=10)


class ChatCitationResponse(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_version_id: UUID
    document_title: str
    excerpt: str
    score: float


class ChatQueryResponse(BaseModel):
    answer: str
    citations: list[ChatCitationResponse] = Field(default_factory=list)
    source_types: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    refused: bool = False
    refusal_reason: str | None = None


class ChatQueryLogResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    user_id: UUID
    question: str
    answer: str
    refused: bool
    refusal_reason: str | None
    confidence: float
    citations_json: str
    source_types_json: str
    created_at: datetime
