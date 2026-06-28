from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.disciplinary.models import DisciplinaryRecord


class DisciplinaryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, record: DisciplinaryRecord) -> DisciplinaryRecord:
        self._db.add(record)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def get_by_id(self, tenant_id: UUID, record_id: UUID) -> DisciplinaryRecord | None:
        result = await self._db.execute(
            select(DisciplinaryRecord).where(
                DisciplinaryRecord.tenant_id == tenant_id,
                DisciplinaryRecord.id == record_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(self, tenant_id: UUID) -> list[DisciplinaryRecord]:
        result = await self._db.execute(
            select(DisciplinaryRecord)
            .where(DisciplinaryRecord.tenant_id == tenant_id)
            .order_by(DisciplinaryRecord.recorded_at.desc())
        )
        return list(result.scalars().all())

    async def list_by_membership_profile(self, tenant_id: UUID, membership_profile_id: UUID) -> list[DisciplinaryRecord]:
        result = await self._db.execute(
            select(DisciplinaryRecord)
            .where(
                DisciplinaryRecord.tenant_id == tenant_id,
                DisciplinaryRecord.membership_profile_id == membership_profile_id,
            )
            .order_by(DisciplinaryRecord.recorded_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, tenant_id: UUID, record_id: UUID, data: dict) -> DisciplinaryRecord | None:
        record = await self.get_by_id(tenant_id, record_id)
        if not record:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(record, key, value)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def delete(self, tenant_id: UUID, record_id: UUID) -> bool:
        record = await self.get_by_id(tenant_id, record_id)
        if not record:
            return False
        await self._db.delete(record)
        await self._db.flush()
        return True
