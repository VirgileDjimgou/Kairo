from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.capabilities import CAP_EVENTS_SPORTS_WRITE, CAP_EVENTS_WRITE
from app.core.dependencies import AuthDep, DbDep
from app.core.module_guard import require_module
from app.modules.events.schemas import EventCreate, EventResponse, EventUpdate
from app.modules.events.service import EventService

router = APIRouter(
    prefix="/sports",
    tags=["sports-events"],
    dependencies=[require_module("events")],
)


def _can_write(current: AuthDep) -> bool:
    return current.has_capability(CAP_EVENTS_SPORTS_WRITE) or current.has_capability(CAP_EVENTS_WRITE)


@router.get("/events", response_model=list[EventResponse])
async def list_sports_events(current: AuthDep, db: DbDep) -> list[EventResponse]:
    if not _can_write(current):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sports workspace access required")
    service = EventService(db)
    return await service.list_sports_events(current.tenant_id)


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_sports_event(event_id: UUID, current: AuthDep, db: DbDep) -> EventResponse:
    if not _can_write(current):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sports workspace access required")
    service = EventService(db)
    return await service.get_sports_event(current.tenant_id, event_id)


@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_sports_event(data: EventCreate, current: AuthDep, db: DbDep) -> EventResponse:
    if not _can_write(current):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sports event write capability required")
    service = EventService(db)
    return await service.create_sports_event(current.tenant_id, data, actor_user_id=current.user.id)


@router.patch("/events/{event_id}", response_model=EventResponse)
async def update_sports_event(
    event_id: UUID,
    data: EventUpdate,
    current: AuthDep,
    db: DbDep,
) -> EventResponse:
    if not _can_write(current):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sports event write capability required")
    service = EventService(db)
    return await service.update_sports_event(current.tenant_id, event_id, data, actor_user_id=current.user.id)


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sports_event(event_id: UUID, current: AuthDep, db: DbDep) -> None:
    if not _can_write(current):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sports event write capability required")
    service = EventService(db)
    await service.delete_sports_event(current.tenant_id, event_id, actor_user_id=current.user.id)
