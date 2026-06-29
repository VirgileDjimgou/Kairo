from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditEvent
from app.modules.audit.repository import AuditRepository
from app.modules.audit.schemas import AuditEventResponse


class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = AuditRepository(db)

    async def record_event(
        self,
        *,
        tenant_id: UUID,
        actor_user_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: UUID | str | None = None,
        module_key: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditEventResponse:
        event = AuditEvent(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action=action.strip(),
            entity_type=entity_type.strip(),
            entity_id=str(entity_id) if entity_id is not None else None,
            module_key=module_key.strip() if module_key else None,
            details_json=self._dump_details(details or {}),
        )
        created = await self._repo.create(event)
        return self._to_response(created)

    async def list_events(
        self,
        tenant_id: UUID,
        *,
        limit: int = 50,
        offset: int = 0,
        actor_user_id: UUID | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        module_key: str | None = None,
        search: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> list[AuditEventResponse]:
        rows = await self._repo.list_events(
            tenant_id,
            limit=limit,
            offset=offset,
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            module_key=module_key,
            search=search,
            created_from=created_from,
            created_to=created_to,
        )
        return [self._to_response(row) for row in rows]

    async def count_events(
        self,
        tenant_id: UUID,
        *,
        actor_user_id: UUID | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        module_key: str | None = None,
        search: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> int:
        return await self._repo.count_events(
            tenant_id,
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            module_key=module_key,
            search=search,
            created_from=created_from,
            created_to=created_to,
        )

    async def export_csv(
        self,
        tenant_id: UUID,
        *,
        actor_user_id: UUID | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        module_key: str | None = None,
        search: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> str:
        rows = await self.list_events(
            tenant_id,
            limit=5000,
            offset=0,
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            module_key=module_key,
            search=search,
            created_from=created_from,
            created_to=created_to,
        )
        buffer = io.StringIO()
        writer = csv.DictWriter(
            buffer,
            fieldnames=[
                "id",
                "tenant_id",
                "actor_user_id",
                "module_key",
                "action",
                "entity_type",
                "entity_id",
                "details_json",
                "created_at",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "id": row.id,
                    "tenant_id": row.tenant_id,
                    "actor_user_id": row.actor_user_id or "",
                    "module_key": row.module_key or "",
                    "action": row.action,
                    "entity_type": row.entity_type,
                    "entity_id": row.entity_id or "",
                    "details_json": json.dumps(row.details, ensure_ascii=False, default=str),
                    "created_at": row.created_at.isoformat(),
                }
            )
        return buffer.getvalue()

    def _to_response(self, event: AuditEvent) -> AuditEventResponse:
        return AuditEventResponse(
            id=event.id,
            tenant_id=event.tenant_id,
            actor_user_id=event.actor_user_id,
            module_key=event.module_key,
            action=event.action,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            details=self._load_details(event.details_json),
            created_at=event.created_at,
        )

    def _dump_details(self, details: dict[str, Any]) -> str:
        return json.dumps(details, ensure_ascii=False, default=self._json_default)

    def _load_details(self, raw: str) -> dict[str, Any]:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        if isinstance(parsed, dict):
            return parsed
        return {"value": parsed}

    def _json_default(self, value: Any) -> Any:
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)

