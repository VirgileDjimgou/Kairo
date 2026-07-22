from __future__ import annotations

import json
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.capabilities import CAP_EVENTS_WRITE
from app.core.dependencies import CurrentUser
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
            metadata_json=self._dump_metadata(data.metadata_json),
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

    async def get_event(
        self,
        tenant_id: UUID,
        event_id: UUID,
        *,
        current: CurrentUser,
    ) -> EventResponse:
        event = await self._repo.get_by_id(tenant_id, event_id)
        if not event or not self._can_view_event(current, event):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )
        return EventResponse.model_validate(event)

    async def get_sports_event(self, tenant_id: UUID, event_id: UUID) -> EventResponse:
        event = await self._get_sports_event_or_404(tenant_id, event_id)
        return EventResponse.model_validate(event)

    async def list_events(
        self, tenant_id: UUID, *, published_only: bool = False
    ) -> list[EventResponse]:
        events = await self._repo.list_by_tenant(tenant_id, published_only=published_only)
        return [EventResponse.model_validate(e) for e in events]

    async def list_sports_events(self, tenant_id: UUID) -> list[EventResponse]:
        events = await self._repo.list_by_tenant(tenant_id)
        return [EventResponse.model_validate(e) for e in events if self._is_sports_event(e)]

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
        payload = data.model_dump(exclude_unset=True)
        if "metadata_json" in payload and payload["metadata_json"] is not None:
            payload["metadata_json"] = self._dump_metadata(payload["metadata_json"])
        event = await self._repo.update(tenant_id, event_id, payload)
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
            details={"changes": payload},
        )
        await self._db.commit()
        return EventResponse.model_validate(event)

    async def update_sports_event(
        self,
        tenant_id: UUID,
        event_id: UUID,
        data: EventUpdate,
        *,
        actor_user_id: UUID | None = None,
    ) -> EventResponse:
        existing = await self._get_sports_event_or_404(tenant_id, event_id)
        payload = data.model_dump(exclude_unset=True)
        if "metadata_json" in payload:
            payload["metadata_json"] = self._dump_metadata(
                self._merge_sports_metadata(existing.metadata_json, payload["metadata_json"])
            )
        else:
            payload["metadata_json"] = self._dump_metadata(
                self._merge_sports_metadata(existing.metadata_json, None)
            )
        event = await self._repo.update(tenant_id, event_id, payload)
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
            details={"changes": payload},
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

    async def delete_sports_event(
        self,
        tenant_id: UUID,
        event_id: UUID,
        *,
        actor_user_id: UUID | None = None,
    ) -> None:
        await self._get_sports_event_or_404(tenant_id, event_id)
        await self.delete_event(tenant_id, event_id, actor_user_id=actor_user_id)

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

    async def create_sports_event(
        self,
        tenant_id: UUID,
        data: EventCreate,
        *,
        actor_user_id: UUID | None = None,
    ) -> EventResponse:
        sports_metadata = self._merge_sports_metadata(None, data.metadata_json)
        sports_payload = EventCreate.model_validate(
            {
                **data.model_dump(),
                "metadata_json": sports_metadata,
            }
        )
        return await self.create_event(tenant_id, sports_payload, actor_user_id=actor_user_id)

    def _is_sports_event(self, event: Event) -> bool:
        metadata = self._parse_metadata(event.metadata_json)
        return metadata.get("workspace") == "sports"

    def _merge_sports_metadata(
        self,
        existing_metadata: str | dict | None,
        incoming_metadata: dict[str, object] | None,
    ) -> dict[str, object]:
        merged = self._parse_metadata(existing_metadata)
        if incoming_metadata:
            merged.update(incoming_metadata)
        merged["workspace"] = "sports"
        return merged

    def _parse_metadata(self, value: str | dict | None) -> dict[str, object]:
        if value in (None, ""):
            return {}
        if isinstance(value, dict):
            return dict(value)
        try:
            parsed = json.loads(value)  # type: ignore[arg-type]
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _dump_metadata(self, value: dict[str, object] | None) -> str:
        return json.dumps(value or {}, ensure_ascii=False, default=str)

    def _can_view_event(self, current: CurrentUser, event: Event) -> bool:
        if current.has_capability(CAP_EVENTS_WRITE):
            return True
        if event.status != "published":
            return False
        if event.visibility_scope == "admin_only":
            return False
        if event.visibility_scope == "role_restricted":
            allowed_role_ids = self._parse_role_ids(event.allowed_role_ids_json)
            return bool(allowed_role_ids.intersection(current.roles))
        return True

    def _parse_role_ids(self, raw: str | None) -> set[str]:
        if not raw:
            return set()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return set()
        if isinstance(parsed, list):
            return {str(item) for item in parsed}
        return set()

    async def _get_sports_event_or_404(self, tenant_id: UUID, event_id: UUID) -> Event:
        event = await self._repo.get_by_id(tenant_id, event_id)
        if not event or not self._is_sports_event(event):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )
        return event
