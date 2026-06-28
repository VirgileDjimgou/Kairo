from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.announcements.models import Announcement
from app.modules.announcements.repository import AnnouncementRepository
from app.modules.announcements.schemas import (
    AnnouncementCreate,
    AnnouncementResponse,
    AnnouncementUpdate,
)


class AnnouncementService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = AnnouncementRepository(db)

    async def create_announcement(
        self, tenant_id: UUID, data: AnnouncementCreate
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
        self, tenant_id: UUID, announcement_id: UUID, data: AnnouncementUpdate
    ) -> AnnouncementResponse:
        announcement = await self._repo.update(
            tenant_id, announcement_id, data.model_dump(exclude_unset=True)
        )
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found",
            )
        return AnnouncementResponse.model_validate(announcement)

    async def delete_announcement(self, tenant_id: UUID, announcement_id: UUID) -> None:
        deleted = await self._repo.delete(tenant_id, announcement_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found",
            )
