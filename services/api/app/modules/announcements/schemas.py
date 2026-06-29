from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.modules.announcements.models import AnnouncementVisibility


class AnnouncementCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=50000)
    visibility_scope: AnnouncementVisibility = AnnouncementVisibility.members_only
    published_at: datetime | None = None
    expires_at: datetime | None = None

    @model_validator(mode="after")
    def _validate_dates(self) -> AnnouncementCreate:
        if self.published_at and self.expires_at and self.published_at >= self.expires_at:
            raise ValueError("expires_at must be after published_at")
        return self


class AnnouncementUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    body: str | None = Field(None, max_length=50000)
    visibility_scope: AnnouncementVisibility | None = None
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
