from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AuditEventResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    actor_user_id: UUID | None
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

