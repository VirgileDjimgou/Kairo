from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AuditActorSummary(BaseModel):
    """Human-readable, tenant-scoped identity of an audit event author."""

    display_name: str
    email: str
    roles: list[str] = Field(default_factory=list)


class AuditEventResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    actor_user_id: UUID | None
    actor: AuditActorSummary | None = None
    module_key: str | None
    action: str
    entity_type: str
    entity_id: str | None
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class AuditEventExportRow(BaseModel):
    id: UUID
    tenant_id: UUID
    actor_user_id: UUID | None
    module_key: str | None
    action: str
    entity_type: str
    entity_id: str | None
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class OperationFailureCreate(BaseModel):
    """A deliberately small, non-sensitive client-side failure report."""

    method: str = Field(min_length=1, max_length=12)
    path: str = Field(min_length=1, max_length=240)
    status_code: int | None = Field(default=None, ge=0, le=599)
