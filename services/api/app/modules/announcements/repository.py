from __future__ import annotations

from datetime import UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.announcements.models import Announcement


class AnnouncementRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, announcement: Announcement) -> Announcement:
        self._db.add(announcement)
        await self._db.flush()
        await self._db.refresh(announcement)
        return announcement

    async def get_by_id(self, tenant_id: UUID, announcement_id: UUID) -> Announcement | None:
        result = await self._db.execute(
            select(Announcement).where(
                Announcement.tenant_id == tenant_id,
                Announcement.id == announcement_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(self, tenant_id: UUID) -> list[Announcement]:
        result = await self._db.execute(
            select(Announcement)
            .where(Announcement.tenant_id == tenant_id)
            .order_by(Announcement.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_active_by_tenant(self, tenant_id: UUID) -> list[Announcement]:
        from datetime import datetime

        now = datetime.now(UTC)
        result = await self._db.execute(
            select(Announcement)
            .where(
                Announcement.tenant_id == tenant_id,
                Announcement.published_at <= now,
                (Announcement.expires_at.is_(None)) | (Announcement.expires_at > now),
            )
            .order_by(Announcement.published_at.desc().nullslast())
        )
        return list(result.scalars().all())

    async def list_visible_active_by_tenant(self, tenant_id: UUID) -> list[Announcement]:
        """Return active announcements that are not admin_only."""
        from datetime import datetime

        now = datetime.now(UTC)
        result = await self._db.execute(
            select(Announcement)
            .where(
                Announcement.tenant_id == tenant_id,
                Announcement.published_at <= now,
                (Announcement.expires_at.is_(None)) | (Announcement.expires_at > now),
                Announcement.visibility_scope != "admin_only",
            )
            .order_by(Announcement.published_at.desc().nullslast())
        )
        return list(result.scalars().all())

    async def update(
        self, tenant_id: UUID, announcement_id: UUID, data: dict
    ) -> Announcement | None:
        announcement = await self.get_by_id(tenant_id, announcement_id)
        if not announcement:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(announcement, key, value)
        await self._db.flush()
        await self._db.refresh(announcement)
        return announcement

    async def delete(self, tenant_id: UUID, announcement_id: UUID) -> bool:
        announcement = await self.get_by_id(tenant_id, announcement_id)
        if not announcement:
            return False
        await self._db.delete(announcement)
        await self._db.flush()
        return True
