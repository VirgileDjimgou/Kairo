from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    start_at: datetime
    end_at: datetime | None = None
    location: str | None = Field(default=None, max_length=255)
    visibility_scope: str = "members_only"
    status: str = "published"


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    location: str | None = Field(default=None, max_length=255)
    visibility_scope: str | None = None
    status: str | None = None


class EventResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    title: str
    description: str | None
    start_at: datetime
    end_at: datetime | None
    location: str | None
    visibility_scope: str
    status: str
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
