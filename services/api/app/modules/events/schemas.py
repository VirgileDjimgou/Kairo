from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.modules.events.models import EventStatus, EventVisibility


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(None, max_length=10000)
    start_at: datetime
    end_at: datetime | None = None
    location: str | None = Field(default=None, max_length=255)
    visibility_scope: EventVisibility = EventVisibility.members_only
    status: EventStatus = EventStatus.published

    @model_validator(mode="after")
    def _validate_dates(self) -> EventCreate:
        if self.end_at and self.start_at >= self.end_at:
            raise ValueError("end_at must be after start_at")
        return self


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=10000)
    start_at: datetime | None = None
    end_at: datetime | None = None
    location: str | None = Field(default=None, max_length=255)
    visibility_scope: EventVisibility | None = None
    status: EventStatus | None = None


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
