from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.modules.contributions.models import ContributionStatus
from app.modules.contributions.schemas import (
    ContributionRecordCreate,
    ContributionRecordResponse,
    ContributionRecordUpdate,
    PaymentRecordCreate,
    PaymentRecordResponse,
    PaymentReversalRequest,
)
from app.modules.domain_events.events import AGGREGATE_PAYMENT, PAYMENT_RECORDED
from app.modules.finance.base import FinanceServiceBase
from app.modules.finance.ledger import as_decimal, derive_contribution_status
from app.modules.membership.repository import MembershipRepository
from app.modules.tenancy.currency import normalize_currency
from app.modules.tenancy.models import Tenant


class ContributionRecordsMixin(FinanceServiceBase):

    async def next_receipt_number(self, tenant_id: UUID, year: int) -> str:
        """Allocate the next per-tenant, per-year receipt number."""
        sequence = await self._repo.increment_receipt_counter(tenant_id, year)
        return f"{year}-{sequence:05d}"

    async def create_contribution(
        self,
        tenant_id: UUID,
        data: ContributionRecordCreate,
        *,
        actor_user_id: UUID | None = None,
    ) -> ContributionRecordResponse:
        tenant_currency = await self.tenant_currency(tenant_id)
        await self.ensure_year_open(tenant_id, data.year)
        existing = await self._repo.get_contribution_by_member_year(
            tenant_id, data.membership_profile_id, data.year
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A contribution already exists for this member and exercise. "
                    "Update it instead of creating a duplicate."
                ),
            )
        requested_currency = (
            data.currency if "currency" in getattr(data, "model_fields_set", set()) else None
        )
        currency = self.resolve_currency(requested_currency, tenant_currency)

        explicit_status = (
            data.status.value if "status" in getattr(data, "model_fields_set", set()) else None
        )
        waived = explicit_status == ContributionStatus.waived.value
        opening_paid = as_decimal(data.paid_amount)

        if opening_paid > 0 and waived:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A waived contribution cannot carry a payment",
            )

        derived = derive_contribution_status(
            expected=as_decimal(data.expected_amount),
            paid=opening_paid,
            due_date=data.due_date,
            waived=False,
        )
        if explicit_status is not None and explicit_status not in {
            ContributionStatus.waived.value,
            derived,
        }:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Contribution status is derived from recorded payments; "
                    f"expected '{derived}' for this record"
                ),
            )

        payload = data.model_dump()
        payload.pop("currency", None)
        payload["currency"] = currency
        payload["paid_amount"] = Decimal("0.00")
        payload["balance"] = as_decimal(data.expected_amount)
        payload["status"] = (
            ContributionStatus.waived.value if waived else ContributionStatus.pending.value
        )

        record = await self._repo.create_contribution(tenant_id, payload)

        if opening_paid > 0:
            # An opening balance is a real payment, not a free-floating amount. It is
            # dated at the end of the contribution year so it lands in the right
            # exercise and can be explained by the treasurer.
            await self._repo.create_payment(
                tenant_id,
                {
                    "contribution_record_id": record.id,
                    "amount": opening_paid,
                    "currency": currency,
                    "paid_at": datetime(record.year, 12, 31, 23, 59, 59, tzinfo=UTC),
                    "payment_method": "other",
                    "reference": "opening balance",
                    "recorded_by": actor_user_id,
                    "metadata_json": '{"source":"opening_balance"}',
                },
            )
            record = await self.sync_contribution_totals(tenant_id, record)

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
                "currency": record.currency,
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
        record = await self._repo.get_contribution(tenant_id, contribution_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contribution record not found",
            )
        await self.ensure_year_open(tenant_id, record.year)

        changes = data.model_dump(exclude_unset=True)
        target_year = changes.get("year", record.year)
        if target_year != record.year:
            await self.ensure_year_open(tenant_id, int(target_year))
        if changes.get("paid_amount") is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "paid_amount is derived from recorded payments. "
                    "Record a payment or reverse an existing one instead."
                ),
            )
        changes.pop("paid_amount", None)

        requested_currency = changes.pop("currency", None)
        if requested_currency is not None:
            tenant_currency = await self.tenant_currency(tenant_id)
            resolved_currency = self.resolve_currency(requested_currency, tenant_currency)
            if resolved_currency != record.currency:
                if await self._repo.count_payments(tenant_id, contribution_id) > 0:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Currency cannot change once payments are recorded",
                    )
                changes["currency"] = resolved_currency

        requested_status = changes.pop("status", None)
        if requested_status is not None:
            requested_value = (
                requested_status.value
                if hasattr(requested_status, "value")
                else str(requested_status)
            )
            record_is_waived = record.status == ContributionStatus.waived.value
            derived = derive_contribution_status(
                expected=as_decimal(changes.get("expected_amount", record.expected_amount)),
                paid=as_decimal(record.paid_amount),
                due_date=changes.get("due_date", record.due_date),
                waived=record_is_waived,
            )
            if requested_value == ContributionStatus.waived.value:
                changes["status"] = ContributionStatus.waived.value
            elif record_is_waived and requested_value == ContributionStatus.pending.value:
                # Re-activate a waived contribution: the derived status is applied by
                # the synchronisation step below.
                changes["status"] = ContributionStatus.pending.value
            elif requested_value != derived:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        "Contribution status is derived from recorded payments; "
                        f"expected '{derived}'"
                    ),
                )

        updated = await self._repo.update_contribution(tenant_id, contribution_id, changes)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contribution record not found",
            )
        updated = await self.sync_contribution_totals(tenant_id, updated)

        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="update",
            entity_type="contribution_record",
            entity_id=updated.id,
            module_key="contributions",
            details={"changes": data.model_dump(exclude_unset=True)},
        )
        await self._db.commit()
        return ContributionRecordResponse.model_validate(updated)

    async def delete_contribution(
        self,
        tenant_id: UUID,
        contribution_id: UUID,
        *,
        actor_user_id: UUID | None = None,
    ) -> None:
        existing = await self._repo.get_contribution(tenant_id, contribution_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contribution record not found",
            )
        await self.ensure_year_open(tenant_id, existing.year)
        payment_count = await self._repo.count_payments(tenant_id, contribution_id)
        if payment_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"This contribution has {payment_count} recorded payment(s). "
                    "Reverse the payments instead of deleting the record."
                ),
            )
        declaration_count = await self._repo.count_receipt_declarations_for_contribution(
            tenant_id, contribution_id
        )
        if declaration_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"This contribution is linked to {declaration_count} receipt "
                    "declaration(s) and cannot be deleted."
                ),
            )

        await self._repo.delete_contribution(tenant_id, contribution_id)
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="delete",
            entity_type="contribution_record",
            entity_id=contribution_id,
            module_key="contributions",
            details={
                "year": existing.year,
                "membership_profile_id": existing.membership_profile_id,
                "expected_amount": str(existing.expected_amount),
                "paid_amount": str(existing.paid_amount),
                "currency": existing.currency,
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
        if data.idempotency_key:
            existing_payment = await self._repo.get_payment_by_idempotency_key(
                tenant_id, data.idempotency_key
            )
            if existing_payment is not None:
                if (
                    existing_payment.contribution_record_id != data.contribution_record_id
                    or as_decimal(existing_payment.amount) != as_decimal(data.amount)
                ):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            "This idempotency key is already used by a different "
                            "payment"
                        ),
                    )
                return PaymentRecordResponse.model_validate(existing_payment)

        contribution = await self._repo.lock_contribution(
            tenant_id, data.contribution_record_id
        )
        if not contribution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contribution record not found",
            )

        tenant_currency = await self.tenant_currency(tenant_id)
        requested_currency = (
            data.currency if "currency" in getattr(data, "model_fields_set", set()) else None
        )
        if normalize_currency(requested_currency) not in {None, contribution.currency}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Payment currency must match the contribution currency "
                    f"{contribution.currency}"
                ),
            )
        if contribution.currency != tenant_currency:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Contribution currency {contribution.currency} no longer matches "
                    f"the organization currency {tenant_currency}"
                ),
            )

        payload = data.model_dump()
        payload["currency"] = contribution.currency
        if payload.get("paid_at") is None:
            payload["paid_at"] = datetime.now(UTC)
        await self.ensure_year_open(tenant_id, payload["paid_at"].year)
        payload["amount"] = as_decimal(data.amount)
        payload["recorded_by"] = actor_user_id
        payload["account_id"] = await self.resolve_account_id(
            tenant_id, payload.get("account_id"), payload["payment_method"]
        )
        payload["receipt_number"] = await self.next_receipt_number(
            tenant_id, payload["paid_at"].year
        )

        try:
            payment = await self._repo.create_payment(tenant_id, payload)
        except IntegrityError:
            # Two identical submissions raced on the idempotency key: keep a single
            # payment and return the one that won.
            await self._db.rollback()
            existing_payment = await self._repo.get_payment_by_idempotency_key(
                tenant_id, data.idempotency_key or ""
            )
            if existing_payment is None:
                raise
            return PaymentRecordResponse.model_validate(existing_payment)

        await self.sync_contribution_totals(tenant_id, contribution)

        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="payment_recorded",
            entity_type="payment_record",
            entity_id=payment.id,
            module_key="contributions",
            details={
                "contribution_record_id": contribution.id,
                "amount": str(payment.amount),
                "currency": payment.currency,
                "method": payment.payment_method,
                "idempotency_key": payment.idempotency_key,
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
                "membership_profile_id": contribution.membership_profile_id,
                "contribution_record_id": contribution.id,
                "amount": str(payment.amount),
                "currency": payment.currency,
            },
        )
        await self._db.commit()
        return PaymentRecordResponse.model_validate(payment)

    async def reverse_payment(
        self,
        tenant_id: UUID,
        payment_id: UUID,
        data: PaymentReversalRequest,
        *,
        actor_user_id: UUID | None = None,
    ) -> PaymentRecordResponse:
        payment = await self._repo.get_payment(tenant_id, payment_id)
        if payment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )
        if payment.reversed_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Payment is already reversed",
            )
        await self.ensure_year_open(tenant_id, payment.paid_at.year)
        contribution = await self._repo.lock_contribution(
            tenant_id, payment.contribution_record_id
        )
        if contribution is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Payment has no contribution record",
            )

        reversed_payment = await self._repo.update_payment(
            tenant_id,
            payment_id,
            {
                "reversed_at": datetime.now(UTC),
                "reversed_by": actor_user_id,
                "reversal_reason": data.reason,
            },
        )
        assert reversed_payment is not None
        await self.sync_contribution_totals(tenant_id, contribution)

        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="payment_reversed",
            entity_type="payment_record",
            entity_id=reversed_payment.id,
            module_key="contributions",
            details={
                "contribution_record_id": contribution.id,
                "amount": str(reversed_payment.amount),
                "currency": reversed_payment.currency,
                "reason": data.reason,
            },
        )
        await self._db.commit()
        return PaymentRecordResponse.model_validate(reversed_payment)

    async def build_payment_receipt(
        self,
        tenant_id: UUID,
        payment_id: UUID,
        *,
        user_id: UUID,
        can_read_tenant: bool,
    ) -> tuple[bytes, str]:
        """Build the numbered payment receipt (quittance) as a PDF."""
        import io

        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        payment = await self._repo.get_payment(tenant_id, payment_id)
        if payment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )
        if payment.reversed_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A reversed payment cannot produce a receipt",
            )
        contribution = await self._repo.get_contribution(
            tenant_id, payment.contribution_record_id
        )
        if contribution is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Payment has no contribution record",
            )
        profile = await MembershipRepository(self._db).get_by_id(
            tenant_id, contribution.membership_profile_id
        )
        if not can_read_tenant and (profile is None or profile.user_id != user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only download your own receipts",
            )
        tenant = await self._db.get(Tenant, tenant_id)

        output = io.BytesIO()
        document = SimpleDocTemplate(
            output,
            pagesize=A4,
            leftMargin=20 * mm,
            rightMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            title=f"Receipt {payment.receipt_number or payment.id}",
        )
        styles = getSampleStyleSheet()
        story = [
            Paragraph(tenant.name if tenant else "Association", styles["Title"]),
            Spacer(1, 4 * mm),
            Paragraph("Quittance de paiement", styles["Heading2"]),
            Spacer(1, 6 * mm),
        ]
        rows = [
            ["Numero", payment.receipt_number or "Non numerote"],
            ["Date", payment.paid_at.strftime("%d.%m.%Y")],
            [
                "Membre",
                (
                    f"{profile.member_code} - {profile.display_name}"
                    if profile is not None
                    else contribution.membership_profile_id
                ),
            ],
            ["Exercice", str(contribution.year)],
            ["Montant", f"{payment.amount} {payment.currency}"],
            ["Moyen", payment.payment_method],
            ["Reference", payment.reference or "-"],
        ]
        table = Table(rows, colWidths=[40 * mm, 120 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.25, "#CCCCCC"),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 10 * mm))
        story.append(
            Paragraph(
                "Document genere par Kairo. Conservez cette quittance comme preuve de paiement.",
                styles["Italic"],
            )
        )
        document.build(story)
        filename = f"quittance-{payment.receipt_number or payment.id}.pdf"
        return output.getvalue(), filename

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
