from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AnnouncementCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)
    visibility_scope: str = "members_only"
    published_at: datetime | None = None
    expires_at: datetime | None = None


class AnnouncementUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    body: str | None = None
    visibility_scope: str | None = None
    published_at: datetime | None = None
    expires_at: datetime | None = None


class AnnouncementResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    title: str
    body: str
    visibility_scope: str
    published_at: datetime | None
    expires_at: datetime | None
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
