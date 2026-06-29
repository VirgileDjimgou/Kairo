from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.policies.models import PolicyStatus


class PolicyRecordCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    description: str | None = Field(None, max_length=10000)
    document_id: UUID | None = None
    status: PolicyStatus = PolicyStatus.published


class PolicyRecordUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=10000)
    document_id: UUID | None = None
    status: PolicyStatus | None = None


class PolicyRecordResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    title: str
    category: str
    description: str | None
    document_id: UUID | None
    document_title: str | None = None
    status: str
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PolicyCategoryResponse(BaseModel):
    categories: list[str] = Field(default_factory=list)
