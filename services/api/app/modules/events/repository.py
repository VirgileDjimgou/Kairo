from __future__ import annotations

from datetime import UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.events.models import Event


class EventRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, event: Event) -> Event:
        self._db.add(event)
        await self._db.flush()
        await self._db.refresh(event)
        return event

    async def get_by_id(self, tenant_id: UUID, event_id: UUID) -> Event | None:
        result = await self._db.execute(
            select(Event).where(
                Event.tenant_id == tenant_id,
                Event.id == event_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self, tenant_id: UUID, *, published_only: bool = False
    ) -> list[Event]:
        query = select(Event).where(Event.tenant_id == tenant_id)
        if published_only:
            query = query.where(Event.status == "published")
        query = query.order_by(Event.start_at.desc())
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def list_visible_by_tenant(self, tenant_id: UUID) -> list[Event]:
        """Return published events that are not admin_only."""
        result = await self._db.execute(
            select(Event).where(
                Event.tenant_id == tenant_id,
                Event.status == "published",
                Event.visibility_scope != "admin_only",
            ).order_by(Event.start_at.asc())
        )
        return list(result.scalars().all())

    async def list_upcoming_by_tenant(
        self, tenant_id: UUID, *, published_only: bool = False
    ) -> list[Event]:
        from datetime import datetime

        now = datetime.now(UTC)
        query = select(Event).where(
            Event.tenant_id == tenant_id,
            Event.start_at >= now,
        )
        if published_only:
            query = query.where(Event.status == "published")
        query = query.order_by(Event.start_at.asc())
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def update(self, tenant_id: UUID, event_id: UUID, data: dict) -> Event | None:
        event = await self.get_by_id(tenant_id, event_id)
        if not event:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(event, key, value)
        await self._db.flush()
        await self._db.refresh(event)
        return event

    async def delete(self, tenant_id: UUID, event_id: UUID) -> bool:
        event = await self.get_by_id(tenant_id, event_id)
        if not event:
            return False
        await self._db.delete(event)
        await self._db.flush()
        return True
