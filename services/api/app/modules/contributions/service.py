from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.import_export import ImportResult, ImportRowError, generate_csv, parse_csv
from app.modules.audit.service import AuditService
from app.modules.contributions.repository import ContributionRepository
from app.modules.contributions.schemas import (
    ContributionRecordCreate,
    ContributionRecordResponse,
    ContributionRecordUpdate,
    PaymentRecordCreate,
    PaymentRecordResponse,
)
from app.modules.membership.repository import MembershipRepository


class ContributionService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = ContributionRepository(db)
        self._audit = AuditService(db)

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
            from datetime import datetime, timezone
            payload["paid_at"] = datetime.now(timezone.utc)
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
        await self._db.commit()
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

    async def import_csv(
        self,
        tenant_id: UUID,
        content: bytes,
        *,
        dry_run: bool = False,
        actor_user_id: UUID | None = None,
    ) -> ImportResult:
        rows = parse_csv(content)
        member_repo = MembershipRepository(self._db)
        errors: list[ImportRowError] = []
        success_count = 0

        for i, row in enumerate(rows, start=2):
            row_errors: list[ImportRowError] = []

            member_code = row.get("member_code", "").strip()
            year_str = row.get("year", "").strip()
            expected_str = row.get("expected_amount", "0").strip()
            paid_str = row.get("paid_amount", "0").strip()
            currency = row.get("currency", "EUR").strip().upper()
            status_val = row.get("status", "pending").strip()

            if not member_code:
                row_errors.append(ImportRowError(row_number=i, column="member_code", message="member_code is required"))

            year: int | None = None
            try:
                year = int(year_str)
                if year < 2000 or year > 2100:
                    row_errors.append(ImportRowError(row_number=i, column="year", message="year must be between 2000 and 2100"))
            except (ValueError, TypeError):
                row_errors.append(ImportRowError(row_number=i, column="year", message="year must be an integer"))

            expected = Decimal("0")
            paid = Decimal("0")
            try:
                expected = Decimal(expected_str)
                if expected < 0:
                    row_errors.append(ImportRowError(row_number=i, column="expected_amount", message="expected_amount must be >= 0"))
            except Exception:
                row_errors.append(ImportRowError(row_number=i, column="expected_amount", message="expected_amount must be a valid number"))

            try:
                paid = Decimal(paid_str)
                if paid < 0:
                    row_errors.append(ImportRowError(row_number=i, column="paid_amount", message="paid_amount must be >= 0"))
            except Exception:
                row_errors.append(ImportRowError(row_number=i, column="paid_amount", message="paid_amount must be a valid number"))

            if status_val not in ("pending", "partial", "paid", "overdue", "waived"):
                row_errors.append(ImportRowError(row_number=i, column="status", message=f"Invalid status '{status_val}'"))

            if not row_errors:
                profile = await member_repo.get_by_member_code(tenant_id, member_code)
                if not profile:
                    row_errors.append(ImportRowError(
                        row_number=i, column="member_code", message=f"Unknown member_code '{member_code}'"
                    ))

            if row_errors:
                errors.extend(row_errors)
                continue

            if dry_run:
                success_count += 1
                continue

            data = ContributionRecordCreate(
                membership_profile_id=profile.id,
                year=year,
                expected_amount=expected,
                paid_amount=paid,
                currency=currency,
                status=status_val,
            )
            record = await self._repo.create_contribution(tenant_id, data.model_dump())
            await self._audit.record_event(
                tenant_id=tenant_id,
                actor_user_id=actor_user_id,
                action="import",
                entity_type="contribution_record",
                entity_id=record.id,
                module_key="contributions",
                details={"member_code": member_code, "year": year, "source": "csv_import"},
            )
            success_count += 1

        if not dry_run:
            await self._db.commit()

        return ImportResult(
            total_rows=len(rows),
            success_count=success_count,
            error_count=len(errors),
            errors=errors,
            dry_run=dry_run,
        )

    async def export_csv(self, tenant_id: UUID) -> str:
        records = await self._repo.list_by_tenant(tenant_id)
        rows = [
            {
                "membership_profile_id": str(r.membership_profile_id),
                "year": str(r.year),
                "expected_amount": str(r.expected_amount),
                "paid_amount": str(r.paid_amount),
                "balance": str(r.balance),
                "currency": r.currency,
                "status": r.status,
                "due_date": str(r.due_date) if r.due_date else "",
            }
            for r in records
        ]
        return generate_csv(rows)
