from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.import_export import generate_csv
from app.modules.audit.service import AuditService
from app.modules.announcements.models import Announcement
from app.modules.announcements.repository import AnnouncementRepository
from app.modules.announcements.schemas import (
    AnnouncementCreate,
    AnnouncementResponse,
    AnnouncementUpdate,
)


class AnnouncementService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = AnnouncementRepository(db)
        self._audit = AuditService(db)

    async def create_announcement(
        self,
        tenant_id: UUID,
        data: AnnouncementCreate,
        *,
        actor_user_id: UUID | None = None,
    ) -> AnnouncementResponse:
        from datetime import datetime, timezone

        announcement = Announcement(
            tenant_id=tenant_id,
            title=data.title,
            body=data.body,
            visibility_scope=data.visibility_scope,
            published_at=data.published_at or datetime.now(timezone.utc),
            expires_at=data.expires_at,
        )
        created = await self._repo.create(announcement)
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="create",
            entity_type="announcement",
            entity_id=created.id,
            module_key="announcements",
            details={
                "title": created.title,
                "visibility_scope": created.visibility_scope,
            },
        )
        await self._db.commit()
        return AnnouncementResponse.model_validate(created)

    async def get_announcement(
        self, tenant_id: UUID, announcement_id: UUID
    ) -> AnnouncementResponse:
        announcement = await self._repo.get_by_id(tenant_id, announcement_id)
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found",
            )
        return AnnouncementResponse.model_validate(announcement)

    async def list_announcements(
        self, tenant_id: UUID, *, active_only: bool = False
    ) -> list[AnnouncementResponse]:
        if active_only:
            announcements = await self._repo.list_active_by_tenant(tenant_id)
        else:
            announcements = await self._repo.list_by_tenant(tenant_id)
        return [AnnouncementResponse.model_validate(a) for a in announcements]

    async def list_visible_announcements(
        self, tenant_id: UUID, *, is_admin: bool = False
    ) -> list[AnnouncementResponse]:
        """Return active announcements the user is allowed to see."""
        if is_admin:
            announcements = await self._repo.list_active_by_tenant(tenant_id)
        else:
            announcements = await self._repo.list_visible_active_by_tenant(tenant_id)
        return [AnnouncementResponse.model_validate(a) for a in announcements]

    async def update_announcement(
        self,
        tenant_id: UUID,
        announcement_id: UUID,
        data: AnnouncementUpdate,
        *,
        actor_user_id: UUID | None = None,
    ) -> AnnouncementResponse:
        announcement = await self._repo.update(
            tenant_id, announcement_id, data.model_dump(exclude_unset=True)
        )
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found",
            )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="update",
            entity_type="announcement",
            entity_id=announcement.id,
            module_key="announcements",
            details={"changes": data.model_dump(exclude_unset=True)},
        )
        await self._db.commit()
        return AnnouncementResponse.model_validate(announcement)

    async def delete_announcement(
        self,
        tenant_id: UUID,
        announcement_id: UUID,
        *,
        actor_user_id: UUID | None = None,
    ) -> None:
        existing = await self._repo.get_by_id(tenant_id, announcement_id)
        deleted = await self._repo.delete(tenant_id, announcement_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found",
            )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="delete",
            entity_type="announcement",
            entity_id=announcement_id,
            module_key="announcements",
            details={"title": existing.title if existing else None},
        )
        await self._db.commit()

    async def export_csv(self, tenant_id: UUID) -> str:
        announcements = await self._repo.list_by_tenant(tenant_id)
        rows = [
            {
                "title": a.title,
                "body": a.body,
                "visibility_scope": a.visibility_scope,
                "published_at": str(a.published_at) if a.published_at else "",
                "expires_at": str(a.expires_at) if a.expires_at else "",
                "status": "active" if a.published_at and (not a.expires_at or a.expires_at > datetime.now(timezone.utc)) else "expired",
            }
            for a in announcements
        ]
        return generate_csv(rows)
