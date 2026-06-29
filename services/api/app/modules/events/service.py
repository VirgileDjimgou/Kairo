from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.import_export import generate_csv
from app.modules.audit.service import AuditService
from app.modules.events.models import Event
from app.modules.events.repository import EventRepository
from app.modules.events.schemas import EventCreate, EventResponse, EventUpdate


class EventService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = EventRepository(db)
        self._audit = AuditService(db)

    async def create_event(
        self,
        tenant_id: UUID,
        data: EventCreate,
        *,
        actor_user_id: UUID | None = None,
    ) -> EventResponse:
        event = Event(
            tenant_id=tenant_id,
            title=data.title,
            description=data.description,
            start_at=data.start_at,
            end_at=data.end_at,
            location=data.location,
            visibility_scope=data.visibility_scope,
            status=data.status,
        )
        created = await self._repo.create(event)
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="create",
            entity_type="event",
            entity_id=created.id,
            module_key="events",
            details={
                "title": created.title,
                "status": created.status,
                "visibility_scope": created.visibility_scope,
            },
        )
        await self._db.commit()
        return EventResponse.model_validate(created)

    async def get_event(self, tenant_id: UUID, event_id: UUID) -> EventResponse:
        event = await self._repo.get_by_id(tenant_id, event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )
        return EventResponse.model_validate(event)

    async def list_events(
        self, tenant_id: UUID, *, published_only: bool = False
    ) -> list[EventResponse]:
        events = await self._repo.list_by_tenant(tenant_id, published_only=published_only)
        return [EventResponse.model_validate(e) for e in events]

    async def list_visible_events(
        self, tenant_id: UUID, *, is_admin: bool = False
    ) -> list[EventResponse]:
        """Return published events the user is allowed to see."""
        if is_admin:
            events = await self._repo.list_by_tenant(tenant_id, published_only=False)
        else:
            events = await self._repo.list_visible_by_tenant(tenant_id)
        return [EventResponse.model_validate(e) for e in events]

    async def list_upcoming_events(
        self, tenant_id: UUID, *, published_only: bool = False
    ) -> list[EventResponse]:
        events = await self._repo.list_upcoming_by_tenant(tenant_id, published_only=published_only)
        return [EventResponse.model_validate(e) for e in events]

    async def update_event(
        self,
        tenant_id: UUID,
        event_id: UUID,
        data: EventUpdate,
        *,
        actor_user_id: UUID | None = None,
    ) -> EventResponse:
        event = await self._repo.update(
            tenant_id, event_id, data.model_dump(exclude_unset=True)
        )
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="update",
            entity_type="event",
            entity_id=event.id,
            module_key="events",
            details={"changes": data.model_dump(exclude_unset=True)},
        )
        await self._db.commit()
        return EventResponse.model_validate(event)

    async def delete_event(
        self,
        tenant_id: UUID,
        event_id: UUID,
        *,
        actor_user_id: UUID | None = None,
    ) -> None:
        existing = await self._repo.get_by_id(tenant_id, event_id)
        deleted = await self._repo.delete(tenant_id, event_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="delete",
            entity_type="event",
            entity_id=event_id,
            module_key="events",
            details={"title": existing.title if existing else None},
        )
        await self._db.commit()

    async def export_csv(self, tenant_id: UUID) -> str:
        events = await self._repo.list_by_tenant(tenant_id)
        rows = [
            {
                "title": e.title,
                "description": e.description or "",
                "start_at": str(e.start_at),
                "end_at": str(e.end_at) if e.end_at else "",
                "location": e.location or "",
                "visibility_scope": e.visibility_scope,
                "status": e.status,
            }
            for e in events
        ]
        return generate_csv(rows)
