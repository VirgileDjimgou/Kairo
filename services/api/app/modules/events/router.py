from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.core.dependencies import AuthDep, DbDep
from app.modules.events.schemas import EventCreate, EventResponse, EventUpdate
from app.modules.events.service import EventService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/public", response_model=list[EventResponse])
async def list_public_events(current: AuthDep, db: DbDep) -> list[EventResponse]:
    """Return published events visible to the authenticated user."""
    service = EventService(db)
    return await service.list_visible_events(
        current.tenant_id, is_admin=current.has_role("admin")
    )


@router.get("/", response_model=list[EventResponse])
async def list_all_events(
    current: AuthDep, db: DbDep, upcoming: bool = Query(default=False)
) -> list[EventResponse]:
    """List all events for the tenant (admin only)."""
    if not current.has_role("admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    service = EventService(db)
    if upcoming:
        return await service.list_upcoming_events(current.tenant_id)
    return await service.list_events(current.tenant_id)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID, current: AuthDep, db: DbDep
) -> EventResponse:
    """Get a specific event."""
    service = EventService(db)
    return await service.get_event(current.tenant_id, event_id)


@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(
    data: EventCreate, current: AuthDep, db: DbDep
) -> EventResponse:
    """Create a new event (admin only)."""
    if not current.has_role("admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    service = EventService(db)
    return await service.create_event(current.tenant_id, data)


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID, data: EventUpdate, current: AuthDep, db: DbDep
) -> EventResponse:
    """Update an event (admin only)."""
    if not current.has_role("admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    service = EventService(db)
    return await service.update_event(current.tenant_id, event_id, data)


@router.delete("/{event_id}", status_code=204)
async def delete_event(event_id: UUID, current: AuthDep, db: DbDep) -> None:
    """Delete an event (admin only)."""
    if not current.has_role("admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    service = EventService(db)
    await service.delete_event(current.tenant_id, event_id)
