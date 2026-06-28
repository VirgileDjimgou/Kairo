from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.membership.models import MembershipProfile


class MembershipRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, tenant_id: UUID, data: dict) -> MembershipProfile:
        profile = MembershipProfile(tenant_id=tenant_id, **data)
        self._db.add(profile)
        await self._db.flush()
        await self._db.refresh(profile)
        return profile

    async def get_by_id(self, tenant_id: UUID, profile_id: UUID) -> MembershipProfile | None:
        result = await self._db.execute(
            select(MembershipProfile).where(
                MembershipProfile.tenant_id == tenant_id,
                MembershipProfile.id == profile_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, tenant_id: UUID, user_id: UUID) -> MembershipProfile | None:
        result = await self._db.execute(
            select(MembershipProfile).where(
                MembershipProfile.tenant_id == tenant_id,
                MembershipProfile.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_member_code(self, tenant_id: UUID, member_code: str) -> MembershipProfile | None:
        result = await self._db.execute(
            select(MembershipProfile).where(
                MembershipProfile.tenant_id == tenant_id,
                MembershipProfile.member_code == member_code,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self, tenant_id: UUID, status: str | None = None
    ) -> list[MembershipProfile]:
        query = select(MembershipProfile).where(
            MembershipProfile.tenant_id == tenant_id
        )
        if status:
            query = query.where(MembershipProfile.status == status)
        query = query.order_by(MembershipProfile.display_name)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def update(
        self, tenant_id: UUID, profile_id: UUID, data: dict
    ) -> MembershipProfile | None:
        profile = await self.get_by_id(tenant_id, profile_id)
        if not profile:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(profile, key, value)
        await self._db.flush()
        await self._db.refresh(profile)
        return profile

    async def delete(self, tenant_id: UUID, profile_id: UUID) -> bool:
        profile = await self.get_by_id(tenant_id, profile_id)
        if not profile:
            return False
        await self._db.delete(profile)
        await self._db.flush()
        return True
