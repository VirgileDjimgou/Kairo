from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.contributions.schemas import (
    ContributionRecordCreate,
    ContributionRecordResponse,
    ContributionRecordUpdate,
    PaymentRecordCreate,
    PaymentRecordResponse,
)
from app.modules.domain_events.events import AGGREGATE_PAYMENT, PAYMENT_RECORDED
from app.modules.finance.base import FinanceServiceBase


class ContributionRecordsMixin(FinanceServiceBase):
    async def create_contribution(
        self,
        tenant_id: UUID,
        data: ContributionRecordCreate,
        *,
        actor_user_id: UUID | None = None,
    ) -> ContributionRecordResponse:
        record = await self._repo.create_contribution(
            tenant_id, data.model_dump()
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="create",
            entity_type="contribution_record",
            entity_id=record.id,
            module_key="contributions",
            details={
                "membership_profile_id": record.membership_profile_id,
                "year": record.year,
                "expected_amount": str(record.expected_amount),
                "paid_amount": str(record.paid_amount),
            },
        )
        await self._db.commit()
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
        self,
        tenant_id: UUID,
        contribution_id: UUID,
        data: ContributionRecordUpdate,
        *,
        actor_user_id: UUID | None = None,
    ) -> ContributionRecordResponse:
        record = await self._repo.update_contribution(
            tenant_id, contribution_id, data.model_dump(exclude_unset=True)
        )
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contribution record not found",
            )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="update",
            entity_type="contribution_record",
            entity_id=record.id,
            module_key="contributions",
            details={"changes": data.model_dump(exclude_unset=True)},
        )
        await self._db.commit()
        return ContributionRecordResponse.model_validate(record)

    async def delete_contribution(
        self,
        tenant_id: UUID,
        contribution_id: UUID,
        *,
        actor_user_id: UUID | None = None,
    ) -> None:
        existing = await self._repo.get_contribution(tenant_id, contribution_id)
        deleted = await self._repo.delete_contribution(tenant_id, contribution_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contribution record not found",
            )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="delete",
            entity_type="contribution_record",
            entity_id=contribution_id,
            module_key="contributions",
            details={
                "year": existing.year if existing else None,
                "membership_profile_id": existing.membership_profile_id if existing else None,
            },
        )
        await self._db.commit()

    async def record_payment(
        self,
        tenant_id: UUID,
        data: PaymentRecordCreate,
        *,
        actor_user_id: UUID | None = None,
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
            payload["paid_at"] = datetime.now(UTC)
        payment = await self._repo.create_payment(tenant_id, payload)
        new_paid = contrib.paid_amount + data.amount
        await self._repo.update_contribution(
            tenant_id, data.contribution_record_id, {"paid_amount": new_paid}
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="payment_recorded",
            entity_type="payment_record",
            entity_id=payment.id,
            module_key="contributions",
            details={
                "contribution_record_id": contrib.id,
                "amount": str(payment.amount),
                "method": payment.payment_method,
            },
        )
        await self._events.publish(
            tenant_id=tenant_id,
            event_type=PAYMENT_RECORDED,
            aggregate_type=AGGREGATE_PAYMENT,
            aggregate_id=payment.id,
            deduplication_key=f"payment-recorded:{payment.id}",
            actor_user_id=actor_user_id,
            payload={
                "membership_profile_id": contrib.membership_profile_id,
                "contribution_record_id": contrib.id,
                "amount": str(payment.amount),
                "currency": payment.currency,
            },
        )
        await self._db.commit()
        return PaymentRecordResponse.model_validate(payment)

    async def list_payments(
        self, tenant_id: UUID, contribution_id: UUID
    ) -> list[PaymentRecordResponse]:
        payments = await self._repo.list_payments_by_contribution(
            tenant_id, contribution_id
        )
        return [PaymentRecordResponse.model_validate(p) for p in payments]

    async def list_tenant_payments(self, tenant_id: UUID) -> list[PaymentRecordResponse]:
        payments = await self._repo.list_payments_by_tenant(tenant_id)
        return [PaymentRecordResponse.model_validate(p) for p in payments]

    async def get_summary(
        self, tenant_id: UUID, year: int | None = None
    ) -> dict:
        return await self._repo.get_tenant_contribution_summary(tenant_id, year)
