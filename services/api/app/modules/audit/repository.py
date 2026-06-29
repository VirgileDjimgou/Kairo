from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditEvent


class AuditRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, event: AuditEvent) -> AuditEvent:
        self._db.add(event)
        await self._db.flush()
        await self._db.refresh(event)
        return event

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
    ) -> list[AuditEvent]:
        query = select(AuditEvent).where(AuditEvent.tenant_id == tenant_id)

        conditions = []
        if actor_user_id is not None:
            conditions.append(AuditEvent.actor_user_id == actor_user_id)
        if action:
            conditions.append(AuditEvent.action == action)
        if entity_type:
            conditions.append(AuditEvent.entity_type == entity_type)
        if entity_id:
            conditions.append(AuditEvent.entity_id == entity_id)
        if module_key:
            conditions.append(AuditEvent.module_key == module_key)
        if created_from is not None:
            conditions.append(AuditEvent.created_at >= created_from)
        if created_to is not None:
            conditions.append(AuditEvent.created_at <= created_to)
        if search:
            pattern = f"%{search.lower()}%"
            conditions.append(
                or_(
                    func.lower(AuditEvent.action).like(pattern),
                    func.lower(AuditEvent.entity_type).like(pattern),
                    func.lower(func.coalesce(AuditEvent.details_json, "")).like(pattern),
                    func.lower(func.coalesce(AuditEvent.entity_id, "")).like(pattern),
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(desc(AuditEvent.created_at), desc(AuditEvent.id)).limit(limit).offset(offset)
        result = await self._db.execute(query)
        return list(result.scalars().all())

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
        query = select(func.count(AuditEvent.id)).where(AuditEvent.tenant_id == tenant_id)
        conditions = []
        if actor_user_id is not None:
            conditions.append(AuditEvent.actor_user_id == actor_user_id)
        if action:
            conditions.append(AuditEvent.action == action)
        if entity_type:
            conditions.append(AuditEvent.entity_type == entity_type)
        if entity_id:
            conditions.append(AuditEvent.entity_id == entity_id)
        if module_key:
            conditions.append(AuditEvent.module_key == module_key)
        if created_from is not None:
            conditions.append(AuditEvent.created_at >= created_from)
        if created_to is not None:
            conditions.append(AuditEvent.created_at <= created_to)
        if search:
            pattern = f"%{search.lower()}%"
            conditions.append(
                or_(
                    func.lower(AuditEvent.action).like(pattern),
                    func.lower(AuditEvent.entity_type).like(pattern),
                    func.lower(func.coalesce(AuditEvent.details_json, "")).like(pattern),
                    func.lower(func.coalesce(AuditEvent.entity_id, "")).like(pattern),
                )
            )
        if conditions:
            query = query.where(and_(*conditions))
        result = await self._db.execute(query)
        return int(result.scalar_one())

