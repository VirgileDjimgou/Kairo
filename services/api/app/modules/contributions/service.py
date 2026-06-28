from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.contributions.repository import ContributionRepository
from app.modules.contributions.schemas import (
    ContributionRecordCreate,
    ContributionRecordResponse,
    ContributionRecordUpdate,
    PaymentRecordCreate,
    PaymentRecordResponse,
)


class ContributionService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = ContributionRepository(db)

    async def create_contribution(
        self, tenant_id: UUID, data: ContributionRecordCreate
    ) -> ContributionRecordResponse:
        record = await self._repo.create_contribution(
            tenant_id, data.model_dump()
        )
        return ContributionRecordResponse.model_validate(record)

    async def get_contribution(
        self, tenant_id: UUID, contribution_id: UUID
    ) -> ContributionRecordResponse:
        record = await self._repo.get_contribution(tenant_id, contribution_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contribution record not found",
            )
        return ContributionRecordResponse.model_validate(record)

    async def list_contributions(
        self, tenant_id: UUID, year: int | None = None
    ) -> list[ContributionRecordResponse]:
        records = await self._repo.list_by_tenant(tenant_id, year)
        return [ContributionRecordResponse.model_validate(r) for r in records]

    async def list_member_contributions(
        self, tenant_id: UUID, profile_id: UUID
    ) -> list[ContributionRecordResponse]:
        records = await self._repo.list_by_profile(tenant_id, profile_id)
        return [ContributionRecordResponse.model_validate(r) for r in records]

    async def update_contribution(
        self, tenant_id: UUID, contribution_id: UUID, data: ContributionRecordUpdate
    ) -> ContributionRecordResponse:
        record = await self._repo.update_contribution(
            tenant_id, contribution_id, data.model_dump(exclude_unset=True)
        )
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contribution record not found",
            )
        return ContributionRecordResponse.model_validate(record)

    async def delete_contribution(self, tenant_id: UUID, contribution_id: UUID) -> None:
        deleted = await self._repo.delete_contribution(tenant_id, contribution_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contribution record not found",
            )

    async def record_payment(
        self, tenant_id: UUID, data: PaymentRecordCreate
    ) -> PaymentRecordResponse:
        contrib = await self._repo.get_contribution(
            tenant_id, data.contribution_record_id
        )
        if not contrib:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contribution record not found",
            )
        payload = data.model_dump()
        if payload.get("paid_at") is None:
            from datetime import datetime, timezone
            payload["paid_at"] = datetime.now(timezone.utc)
        payment = await self._repo.create_payment(tenant_id, payload)
        new_paid = contrib.paid_amount + data.amount
        await self._repo.update_contribution(
            tenant_id, data.contribution_record_id, {"paid_amount": new_paid}
        )
        return PaymentRecordResponse.model_validate(payment)

    async def list_payments(
        self, tenant_id: UUID, contribution_id: UUID
    ) -> list[PaymentRecordResponse]:
        payments = await self._repo.list_payments_by_contribution(
            tenant_id, contribution_id
        )
        return [PaymentRecordResponse.model_validate(p) for p in payments]

    async def get_summary(
        self, tenant_id: UUID, year: int | None = None
    ) -> dict:
        return await self._repo.get_tenant_contribution_summary(tenant_id, year)
