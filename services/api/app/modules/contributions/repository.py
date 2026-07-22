from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.contributions.models import (
    ContributionRecord,
    ContributionReminder,
    PaymentRecord,
)


def _normalize_decimal(value: Decimal) -> Decimal:
    """Round Decimal to 2 places and strip excess trailing zeros."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class ContributionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_contribution(
        self, tenant_id: UUID, data: dict
    ) -> ContributionRecord:
        data["tenant_id"] = tenant_id
        data["balance"] = Decimal(str(data.get("expected_amount", 0))) - Decimal(str(data.get("paid_amount", 0)))
        record = ContributionRecord(**data)
        self._db.add(record)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def get_contribution(
        self, tenant_id: UUID, contribution_id: UUID
    ) -> ContributionRecord | None:
        result = await self._db.execute(
            select(ContributionRecord).where(
                ContributionRecord.tenant_id == tenant_id,
                ContributionRecord.id == contribution_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_profile(
        self, tenant_id: UUID, profile_id: UUID
    ) -> list[ContributionRecord]:
        result = await self._db.execute(
            select(ContributionRecord).where(
                ContributionRecord.tenant_id == tenant_id,
                ContributionRecord.membership_profile_id == profile_id,
            ).order_by(ContributionRecord.year.desc())
        )
        return list(result.scalars().all())

    async def list_by_tenant(
        self, tenant_id: UUID, year: int | None = None
    ) -> list[ContributionRecord]:
        query = select(ContributionRecord).where(
            ContributionRecord.tenant_id == tenant_id
        )
        if year:
            query = query.where(ContributionRecord.year == year)
        query = query.order_by(ContributionRecord.year.desc())
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def update_contribution(
        self, tenant_id: UUID, contribution_id: UUID, data: dict
    ) -> ContributionRecord | None:
        record = await self.get_contribution(tenant_id, contribution_id)
        if not record:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(record, key, value)
        record.balance = record.expected_amount - record.paid_amount
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def delete_contribution(self, tenant_id: UUID, contribution_id: UUID) -> bool:
        record = await self.get_contribution(tenant_id, contribution_id)
        if not record:
            return False
        await self._db.delete(record)
        await self._db.flush()
        return True

    async def create_payment(self, tenant_id: UUID, data: dict) -> PaymentRecord:
        data["tenant_id"] = tenant_id
        record = PaymentRecord(**data)
        self._db.add(record)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def get_payment(
        self, tenant_id: UUID, payment_id: UUID
    ) -> PaymentRecord | None:
        result = await self._db.execute(
            select(PaymentRecord).where(
                PaymentRecord.tenant_id == tenant_id,
                PaymentRecord.id == payment_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_payments_by_contribution(
        self, tenant_id: UUID, contribution_id: UUID
    ) -> list[PaymentRecord]:
        result = await self._db.execute(
            select(PaymentRecord).where(
                PaymentRecord.tenant_id == tenant_id,
                PaymentRecord.contribution_record_id == contribution_id,
            ).order_by(PaymentRecord.paid_at.desc())
        )
        return list(result.scalars().all())

    async def list_payments_by_tenant(
        self, tenant_id: UUID
    ) -> list[PaymentRecord]:
        result = await self._db.execute(
            select(PaymentRecord).where(
                PaymentRecord.tenant_id == tenant_id
            ).order_by(PaymentRecord.paid_at.desc())
        )
        return list(result.scalars().all())

    async def delete_payment(self, tenant_id: UUID, payment_id: UUID) -> bool:
        record = await self.get_payment(tenant_id, payment_id)
        if not record:
            return False
        await self._db.delete(record)
        await self._db.flush()
        return True

    async def create_reminder(self, tenant_id: UUID, data: dict) -> ContributionReminder:
        data["tenant_id"] = tenant_id
        record = ContributionReminder(**data)
        self._db.add(record)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def list_reminders_by_tenant(
        self,
        tenant_id: UUID,
        *,
        year: int | None = None,
        profile_id: UUID | None = None,
        limit: int = 50,
    ) -> list[ContributionReminder]:
        query = select(ContributionReminder).where(
            ContributionReminder.tenant_id == tenant_id
        )
        if profile_id is not None:
            query = query.where(ContributionReminder.membership_profile_id == profile_id)
        if year is not None:
            query = query.join(
                ContributionRecord,
                ContributionRecord.id == ContributionReminder.contribution_record_id,
            ).where(ContributionRecord.year == year)
        query = query.order_by(
            ContributionReminder.sent_at.desc(),
            ContributionReminder.created_at.desc(),
        ).limit(limit)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def get_tenant_contribution_summary(
        self, tenant_id: UUID, year: int | None = None
    ) -> dict:
        query = select(
            func.count(ContributionRecord.id),
            func.coalesce(func.sum(ContributionRecord.expected_amount), 0),
            func.coalesce(func.sum(ContributionRecord.paid_amount), 0),
            func.coalesce(func.sum(ContributionRecord.balance), 0),
        ).where(ContributionRecord.tenant_id == tenant_id)
        if year:
            query = query.where(ContributionRecord.year == year)
        result = await self._db.execute(query)
        row = result.one()
        return {
            "total_count": row[0],
            "total_expected": str(_normalize_decimal(Decimal(str(row[1])))),
            "total_paid": str(_normalize_decimal(Decimal(str(row[2])))),
            "total_balance": str(_normalize_decimal(Decimal(str(row[3])))),
        }
