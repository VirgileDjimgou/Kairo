from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.contributions.models import CashHandoverStatus
from app.modules.contributions.schemas import (
    ContributionReceiptDeclarationResponse,
    ContributionReceiptHandoverReminderUpdate,
    ContributionReceiptHandoverReport,
    ContributionReceiptTreasuryConfirmation,
)
from app.modules.domain_events.events import (
    AGGREGATE_RECEIPT_DECLARATION,
    RECEIPT_HANDOVER_REMINDER_UPDATED,
    RECEIPT_HANDOVER_REPORTED,
    RECEIPT_RECEIVED_IN_TREASURY,
)
from app.modules.finance.base import FinanceServiceBase


class CustodyMixin(FinanceServiceBase):
    async def report_receipt_handover(
        self, tenant_id: UUID, declaration_id: UUID, data: ContributionReceiptHandoverReport, *, declarant_user_id: UUID,
    ) -> ContributionReceiptDeclarationResponse:
        record = await self._repo.get_receipt_declaration(tenant_id, declaration_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt declaration not found")
        if record.declarant_user_id != declarant_user_id or record.cash_handover_status != CashHandoverStatus.pending_handover.value:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Receipt handover cannot be reported")
        updated = await self._repo.update_receipt_declaration(tenant_id, declaration_id, {
            "cash_handover_status": CashHandoverStatus.handover_reported.value,
            "handover_reported_at": datetime.now(UTC), "handover_reported_by_user_id": declarant_user_id,
            "handover_method": data.method, "processing_note": data.note or record.processing_note,
        })
        assert updated is not None
        await self._events.publish(
            tenant_id=tenant_id,
            event_type=RECEIPT_HANDOVER_REPORTED,
            aggregate_type=AGGREGATE_RECEIPT_DECLARATION,
            aggregate_id=updated.id,
            deduplication_key=f"receipt-handover-reported:{updated.id}",
            actor_user_id=declarant_user_id,
            payload={
                "membership_profile_id": updated.membership_profile_id,
                "declarant_user_id": updated.declarant_user_id,
                "audit_details": {"method": data.method},
            },
        )
        await self._db.commit()
        return ContributionReceiptDeclarationResponse.model_validate(updated)

    async def update_receipt_handover_reminder(
        self,
        tenant_id: UUID,
        declaration_id: UUID,
        data: ContributionReceiptHandoverReminderUpdate,
        *,
        treasurer_user_id: UUID,
    ) -> ContributionReceiptDeclarationResponse:
        record = await self._repo.get_receipt_declaration(tenant_id, declaration_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt declaration not found")
        if record.cash_handover_status not in {
            CashHandoverStatus.pending_handover.value,
            CashHandoverStatus.handover_reported.value,
        }:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only an open cash handover reminder can be updated")
        previous_days = record.handover_reminder_days
        now = datetime.now(UTC)
        record.handover_reminder_sent_at = None
        updated = await self._repo.update_receipt_declaration(tenant_id, declaration_id, {
            "handover_reminder_days": data.reminder_days,
            "handover_due_at": now + timedelta(days=data.reminder_days),
            "handover_reminder_updated_at": now,
        })
        assert updated is not None
        await self._events.publish(
            tenant_id=tenant_id,
            event_type=RECEIPT_HANDOVER_REMINDER_UPDATED,
            aggregate_type=AGGREGATE_RECEIPT_DECLARATION,
            aggregate_id=updated.id,
            deduplication_key=f"receipt-handover-reminder:{updated.id}:{now.isoformat()}",
            actor_user_id=treasurer_user_id,
            occurred_at=now,
            payload={
                "amount": str(updated.amount),
                "currency": updated.currency,
                "reminder_days": data.reminder_days,
                "declarant_user_id": updated.declarant_user_id,
                "membership_profile_id": updated.membership_profile_id,
                "audit_details": {
                    "previous_days": previous_days,
                    "reminder_days": data.reminder_days,
                    "due_at": updated.handover_due_at.isoformat(),
                },
            },
        )
        await self._db.commit()
        return ContributionReceiptDeclarationResponse.model_validate(updated)

    async def confirm_receipt_in_treasury(
        self,
        tenant_id: UUID,
        declaration_id: UUID,
        data: ContributionReceiptTreasuryConfirmation,
        *,
        treasurer_user_id: UUID,
    ) -> ContributionReceiptDeclarationResponse:
        record = await self._repo.get_receipt_declaration(tenant_id, declaration_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt declaration not found")
        if record.cash_handover_status not in {
            CashHandoverStatus.pending_handover.value,
            CashHandoverStatus.handover_reported.value,
        }:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only an open cash handover can be closed")
        previous_status = record.cash_handover_status
        updated = await self._repo.update_receipt_declaration(tenant_id, declaration_id, {
            "cash_handover_status": CashHandoverStatus.received_in_treasury.value,
            "handover_method": data.method,
            "treasury_received_at": datetime.now(UTC), "treasury_received_by_user_id": treasurer_user_id,
            "treasury_receipt_note": data.note,
        })
        assert updated is not None
        await self._events.publish(
            tenant_id=tenant_id,
            event_type=RECEIPT_RECEIVED_IN_TREASURY,
            aggregate_type=AGGREGATE_RECEIPT_DECLARATION,
            aggregate_id=updated.id,
            deduplication_key=f"receipt-received-in-treasury:{updated.id}",
            actor_user_id=treasurer_user_id,
            payload={
                "amount": str(updated.amount),
                "currency": updated.currency,
                "declarant_user_id": updated.declarant_user_id,
                "membership_profile_id": updated.membership_profile_id,
                "audit_details": {
                    "closed_from": previous_status,
                    "method": data.method,
                    "note": data.note,
                },
            },
        )
        await self._db.commit()
        return ContributionReceiptDeclarationResponse.model_validate(updated)
