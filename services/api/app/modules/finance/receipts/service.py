from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.contributions.models import (
    CashHandoverStatus,
    ContributionReceiptStatus,
    FinancialIncomeType,
)
from app.modules.contributions.schemas import (
    ContributionReceiptDeclarationCreate,
    ContributionReceiptDeclarationProcess,
    ContributionReceiptDeclarationResponse,
    ContributionReceiptDeclarationUpdate,
)
from app.modules.disciplinary.repository import DisciplinaryRepository
from app.modules.finance.base import FinanceServiceBase
from app.modules.finance.notifications import (
    notify_receipt_declared,
    notify_receipt_processed,
)
from app.modules.membership.repository import MembershipRepository


class ReceiptWorkflowMixin(FinanceServiceBase):
    async def create_receipt_declaration(
        self, tenant_id: UUID, data: ContributionReceiptDeclarationCreate, *,
        declarant_user_id: UUID, declarant_role_code: str,
    ) -> ContributionReceiptDeclarationResponse:
        if data.income_type in {FinancialIncomeType.membership_contribution, FinancialIncomeType.disciplinary_payment}:
            assert data.membership_profile_id is not None
            profile = await MembershipRepository(self._db).get_by_id(tenant_id, data.membership_profile_id)
            if profile is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member profile not found")
        if data.income_type == FinancialIncomeType.disciplinary_payment:
            assert data.disciplinary_record_id is not None and data.membership_profile_id is not None
            disciplinary = await DisciplinaryRepository(self._db).get_by_id(tenant_id, data.disciplinary_record_id)
            if disciplinary is None or disciplinary.membership_profile_id != data.membership_profile_id:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Disciplinary record does not belong to this member")
        payload = data.model_dump()
        payload["received_at"] = payload["received_at"] or datetime.now(UTC)
        payload.update({
            "declarant_user_id": declarant_user_id,
            "declarant_role_code": declarant_role_code,
        })
        record = await self._repo.create_receipt_declaration(tenant_id, payload)
        await notify_receipt_declared(self._db, tenant_id, record=record)
        await self._audit.record_event(
            tenant_id=tenant_id, actor_user_id=declarant_user_id,
            action="receipt_declaration_created", entity_type="contribution_receipt_declaration",
            entity_id=record.id, module_key="contributions",
            details={
                "membership_profile_id": record.membership_profile_id,
                "income_type": record.income_type,
                "source_name": record.source_name,
                "amount": str(record.amount),
            },
        )
        await self._db.commit()
        return ContributionReceiptDeclarationResponse.model_validate(record)

    async def update_receipt_declaration(
        self, tenant_id: UUID, declaration_id: UUID, data: ContributionReceiptDeclarationUpdate,
        *, declarant_user_id: UUID,
    ) -> ContributionReceiptDeclarationResponse:
        record = await self._repo.get_receipt_declaration(tenant_id, declaration_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt declaration not found")
        if record.declarant_user_id != declarant_user_id or record.status not in {
            ContributionReceiptStatus.draft.value, ContributionReceiptStatus.clarification_requested.value,
        }:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Receipt declaration cannot be edited")
        updated = await self._repo.update_receipt_declaration(
            tenant_id, declaration_id, data.model_dump(exclude_unset=True)
        )
        assert updated is not None
        await self._audit.record_event(
            tenant_id=tenant_id, actor_user_id=declarant_user_id,
            action="receipt_declaration_updated", entity_type="contribution_receipt_declaration",
            entity_id=updated.id, module_key="contributions", details={"changes": data.model_dump(exclude_unset=True)},
        )
        await self._db.commit()
        return ContributionReceiptDeclarationResponse.model_validate(updated)

    async def submit_receipt_declaration(
        self, tenant_id: UUID, declaration_id: UUID, *, declarant_user_id: UUID,
    ) -> ContributionReceiptDeclarationResponse:
        record = await self._repo.get_receipt_declaration(tenant_id, declaration_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt declaration not found")
        if record.declarant_user_id != declarant_user_id or record.status not in {
            ContributionReceiptStatus.draft.value, ContributionReceiptStatus.clarification_requested.value,
        }:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Receipt declaration cannot be submitted")
        updated = await self._repo.update_receipt_declaration(tenant_id, declaration_id, {
            "status": ContributionReceiptStatus.submitted.value, "submitted_at": datetime.now(UTC),
            "processing_note": None,
        })
        assert updated is not None
        await self._audit.record_event(
            tenant_id=tenant_id, actor_user_id=declarant_user_id,
            action="receipt_declaration_submitted", entity_type="contribution_receipt_declaration",
            entity_id=updated.id, module_key="contributions", details={},
        )
        await self._db.commit()
        return ContributionReceiptDeclarationResponse.model_validate(updated)

    async def process_receipt_declaration(
        self, tenant_id: UUID, declaration_id: UUID, data: ContributionReceiptDeclarationProcess,
        *, processor_user_id: UUID,
    ) -> ContributionReceiptDeclarationResponse:
        record = await self._repo.get_receipt_declaration(tenant_id, declaration_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt declaration not found")
        if record.status != ContributionReceiptStatus.submitted.value:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only submitted declarations can be processed")
        if data.action in {"rejected", "clarification_requested", "cancelled"} and not data.note:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A processing note is required")
        if data.action in {"validated", "partially_validated"} and record.income_type == FinancialIncomeType.membership_contribution.value:
            if data.contribution_record_id is None:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Contribution record is required")
            amount = data.processed_amount or record.amount
            if amount > record.amount:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Processed amount cannot exceed declared amount")
            if data.action == "validated" and amount != record.amount:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Validated amount must equal declared amount")
            contribution = await self._repo.get_contribution(tenant_id, data.contribution_record_id)
            if contribution is None or contribution.membership_profile_id != record.membership_profile_id:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Contribution record does not belong to this member")
            payment = await self._repo.create_payment(tenant_id, {
                "contribution_record_id": contribution.id, "amount": amount, "currency": record.currency,
                "paid_at": datetime.now(UTC), "payment_method": record.payment_method,
                "reference": record.reference, "recorded_by": processor_user_id,
                "metadata_json": '{"source":"receipt_declaration"}',
            })
            await self._repo.update_contribution(tenant_id, contribution.id, {"paid_amount": contribution.paid_amount + amount})
            updated = await self._repo.update_receipt_declaration(tenant_id, declaration_id, {
                "status": data.action, "processed_at": datetime.now(UTC), "processed_by_user_id": processor_user_id,
                "processed_amount": amount, "processing_note": data.note, "contribution_record_id": contribution.id,
                "payment_record_id": payment.id,
                "cash_handover_status": CashHandoverStatus.pending_handover.value,
                "handover_reminder_days": data.handover_reminder_days,
                "handover_due_at": datetime.now(UTC) + timedelta(days=data.handover_reminder_days),
            })
        elif data.action in {"validated", "partially_validated"}:
            amount = data.processed_amount or record.amount
            if amount > record.amount:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Processed amount cannot exceed declared amount")
            if data.action == "validated" and amount != record.amount:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Validated amount must equal declared amount")
            if record.income_type == FinancialIncomeType.disciplinary_payment.value and data.action == "validated":
                assert record.disciplinary_record_id is not None
                disciplinary = await DisciplinaryRepository(self._db).get_by_id(tenant_id, record.disciplinary_record_id)
                if disciplinary is None or disciplinary.membership_profile_id != record.membership_profile_id:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Disciplinary record does not belong to this member")
                disciplinary.status = "resolved"
            updated = await self._repo.update_receipt_declaration(tenant_id, declaration_id, {
                "status": data.action, "processed_at": datetime.now(UTC), "processed_by_user_id": processor_user_id,
                "processed_amount": amount, "processing_note": data.note,
                "cash_handover_status": CashHandoverStatus.pending_handover.value,
                "handover_reminder_days": data.handover_reminder_days,
                "handover_due_at": datetime.now(UTC) + timedelta(days=data.handover_reminder_days),
            })
        else:
            updated = await self._repo.update_receipt_declaration(tenant_id, declaration_id, {
                "status": data.action, "processed_at": datetime.now(UTC), "processed_by_user_id": processor_user_id,
                "processing_note": data.note,
            })
        assert updated is not None
        await self._audit.record_event(
            tenant_id=tenant_id, actor_user_id=processor_user_id,
            action=f"receipt_declaration_{data.action}", entity_type="contribution_receipt_declaration",
            entity_id=updated.id, module_key="contributions",
            details={"processed_amount": str(updated.processed_amount) if updated.processed_amount else None},
        )
        await notify_receipt_processed(
            self._db, tenant_id, record=record, updated=updated, action=data.action,
        )
        await self._db.commit()
        return ContributionReceiptDeclarationResponse.model_validate(updated)

    async def list_receipt_declarations(
        self, tenant_id: UUID, *, declarant_user_id: UUID | None = None,
        membership_profile_id: UUID | None = None,
    ) -> list[ContributionReceiptDeclarationResponse]:
        rows = await self._repo.list_receipt_declarations(
            tenant_id, declarant_user_id=declarant_user_id, membership_profile_id=membership_profile_id
        )
        return [ContributionReceiptDeclarationResponse.model_validate(row) for row in rows]
