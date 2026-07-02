from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from app.modules.events.models import EventStatus, EventVisibility


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(None, max_length=10000)
    start_at: datetime
    end_at: datetime | None = None
    location: str | None = Field(default=None, max_length=255)
    visibility_scope: EventVisibility = EventVisibility.members_only
    status: EventStatus = EventStatus.published
    metadata_json: dict[str, Any] = Field(default_factory=dict)

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
    metadata_json: dict[str, Any] | None = None


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
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("metadata_json", mode="before")
    @classmethod
    def _parse_metadata_json(cls, value: Any) -> dict[str, Any]:
        if value in (None, ""):
            return {}
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return {}
            return parsed if isinstance(parsed, dict) else {}
        if isinstance(value, dict):
            return value
        return {}
