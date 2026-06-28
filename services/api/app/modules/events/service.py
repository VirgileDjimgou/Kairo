from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.events.models import Event
from app.modules.events.repository import EventRepository
from app.modules.events.schemas import EventCreate, EventResponse, EventUpdate


class EventService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = EventRepository(db)

    async def create_event(self, tenant_id: UUID, data: EventCreate) -> EventResponse:
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
        self, tenant_id: UUID, event_id: UUID, data: EventUpdate
    ) -> EventResponse:
        event = await self._repo.update(
            tenant_id, event_id, data.model_dump(exclude_unset=True)
        )
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )
        return EventResponse.model_validate(event)

    async def delete_event(self, tenant_id: UUID, event_id: UUID) -> None:
        deleted = await self._repo.delete(tenant_id, event_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )
