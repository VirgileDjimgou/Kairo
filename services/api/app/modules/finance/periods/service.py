"""Exercise closing for the treasury ledger."""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.contributions.models import FinancePeriod
from app.modules.contributions.schemas import FinancePeriodResponse
from app.modules.finance.base import FinanceServiceBase


class PeriodsMixin(FinanceServiceBase):
    @staticmethod
    def _to_response(record: FinancePeriod | None, year: int) -> FinancePeriodResponse:
        if record is None:
            return FinancePeriodResponse(year=year, status="open")
        return FinancePeriodResponse(
            year=record.year,
            status="closed" if record.status == "closed" else "open",
            closed_at=record.closed_at,
            closed_by=record.closed_by_user_id,
            reopened_at=record.reopened_at,
            reopen_reason=record.reopen_reason,
        )

    async def list_finance_periods(self, tenant_id: UUID) -> list[FinancePeriodResponse]:
        records = await self._repo.list_finance_periods(tenant_id)
        return [self._to_response(record, record.year) for record in records]

    async def get_finance_period(
        self, tenant_id: UUID, year: int
    ) -> FinancePeriodResponse:
        record = await self._repo.get_finance_period(tenant_id, year)
        return self._to_response(record, year)

    async def close_finance_period(
        self, tenant_id: UUID, year: int, *, actor_user_id: UUID
    ) -> FinancePeriodResponse:
        existing = await self._repo.get_finance_period(tenant_id, year)
        if existing is not None and existing.status == "closed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Exercise {year} is already closed",
            )
        declarations = await self._repo.list_receipt_declarations(tenant_id)
        pending_declarations = [
            declaration
            for declaration in declarations
            if declaration.received_at.year == year
            and declaration.status
            in {
                "submitted",
                "clarification_requested",
            }
        ]
        open_handovers = [
            declaration
            for declaration in declarations
            if declaration.received_at.year == year
            and declaration.cash_handover_status
            in {"pending_handover", "handover_reported"}
        ]
        if pending_declarations or open_handovers:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Exercise {year} cannot be closed: "
                    f"{len(pending_declarations)} declaration(s) still pending and "
                    f"{len(open_handovers)} cash handover(s) not confirmed."
                ),
            )
        now = datetime.now(UTC)
        record = await self._repo.upsert_finance_period(
            tenant_id,
            year,
            {
                "status": "closed",
                "closed_at": now,
                "closed_by_user_id": actor_user_id,
                "reopened_at": None,
                "reopened_by_user_id": None,
                "reopen_reason": None,
            },
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="finance_period_closed",
            entity_type="finance_period",
            entity_id=record.id,
            module_key="contributions",
            details={"year": year},
        )
        await self._db.commit()
        return self._to_response(record, year)

    async def reopen_finance_period(
        self,
        tenant_id: UUID,
        year: int,
        *,
        reason: str,
        actor_user_id: UUID,
    ) -> FinancePeriodResponse:
        existing = await self._repo.get_finance_period(tenant_id, year)
        if existing is None or existing.status != "closed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Exercise {year} is not closed",
            )
        now = datetime.now(UTC)
        record = await self._repo.upsert_finance_period(
            tenant_id,
            year,
            {
                "status": "open",
                "reopened_at": now,
                "reopened_by_user_id": actor_user_id,
                "reopen_reason": reason,
            },
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="finance_period_reopened",
            entity_type="finance_period",
            entity_id=record.id,
            module_key="contributions",
            details={"year": year, "reason": reason},
        )
        await self._db.commit()
        return self._to_response(record, year)
