from __future__ import annotations

from uuid import UUID

from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.policies.models import PolicyRecord


class PolicyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, policy: PolicyRecord) -> PolicyRecord:
        self._db.add(policy)
        await self._db.flush()
        await self._db.refresh(policy)
        return policy

    async def get_by_id(self, tenant_id: UUID, policy_id: UUID) -> PolicyRecord | None:
        result = await self._db.execute(
            select(PolicyRecord).where(
                PolicyRecord.tenant_id == tenant_id,
                PolicyRecord.id == policy_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(self, tenant_id: UUID, *, published_only: bool = False) -> list[PolicyRecord]:
        query = select(PolicyRecord).where(PolicyRecord.tenant_id == tenant_id)
        if published_only:
            query = query.where(PolicyRecord.status == "published")
        result = await self._db.execute(query.order_by(PolicyRecord.category.asc(), PolicyRecord.title.asc()))
        return list(result.scalars().all())

    async def list_categories(self, tenant_id: UUID) -> list[str]:
        result = await self._db.execute(
            select(distinct(PolicyRecord.category))
            .where(PolicyRecord.tenant_id == tenant_id)
            .order_by(PolicyRecord.category.asc())
        )
        return [row[0] for row in result.all() if row[0]]

    async def update(self, tenant_id: UUID, policy_id: UUID, data: dict) -> PolicyRecord | None:
        policy = await self.get_by_id(tenant_id, policy_id)
        if not policy:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(policy, key, value)
        await self._db.flush()
        await self._db.refresh(policy)
        return policy

    async def delete(self, tenant_id: UUID, policy_id: UUID) -> bool:
        policy = await self.get_by_id(tenant_id, policy_id)
        if not policy:
            return False
        await self._db.delete(policy)
        await self._db.flush()
        return True
