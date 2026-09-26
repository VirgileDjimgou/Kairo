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
from app.modules.finance.base import FinanceServiceBase
from app.modules.finance.notifications import dispatch_custody_notice


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
        await self._audit.record_event(tenant_id=tenant_id, actor_user_id=declarant_user_id, action="receipt_handover_reported", entity_type="contribution_receipt_declaration", entity_id=updated.id, module_key="contributions", details={"method": data.method})
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
        await self._audit.record_event(
            tenant_id=tenant_id, actor_user_id=treasurer_user_id,
            action="receipt_handover_reminder_updated", entity_type="contribution_receipt_declaration",
            entity_id=updated.id, module_key="contributions",
            details={"previous_days": previous_days, "reminder_days": data.reminder_days, "due_at": updated.handover_due_at.isoformat()},
        )
        await dispatch_custody_notice(
            self._db, tenant_id, providers=self._notification_providers, record=updated,
            actor_user_id=treasurer_user_id,
            subject="Kairo — délai de remise mis à jour",
            body=f"Le délai de remise en caisse pour l'encaissement de {updated.amount} {updated.currency} a été fixé à {data.reminder_days} jour(s).",
            audit_action="receipt_handover_reminder_notice",
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
        await self._audit.record_event(
            tenant_id=tenant_id, actor_user_id=treasurer_user_id,
            action="receipt_received_in_treasury", entity_type="contribution_receipt_declaration",
            entity_id=updated.id, module_key="contributions",
            details={"closed_from": previous_status, "method": data.method, "note": data.note},
        )
        await dispatch_custody_notice(
            self._db, tenant_id, providers=self._notification_providers, record=updated,
            actor_user_id=treasurer_user_id,
            subject="Kairo — encaissement clôturé",
            body=f"Le trésorier a confirmé la réception en caisse de {updated.amount} {updated.currency}. L'opération est terminée.",
            audit_action="receipt_treasury_closure_notice",
        )
        await self._db.commit()
        return ContributionReceiptDeclarationResponse.model_validate(updated)
