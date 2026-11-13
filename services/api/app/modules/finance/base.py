from typing import Self

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.service import AuditService
from app.modules.contributions.repository import ContributionRepository
from app.modules.domain_events.service import DomainEventService
from app.modules.tenancy.currency import normalize_currency
from app.modules.tenancy.models import Tenant
from app.providers.notifications.base import NotificationProvider


class FinanceServiceBase:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = ContributionRepository(db)
        self._audit = AuditService(db)
        self._events = DomainEventService(db)
        self._notification_providers: list[NotificationProvider] = []

    async def tenant_currency(self, tenant_id) -> str:
        """Return the currency configured by the tenant, defaulting to EUR."""
        from app.modules.tenancy.currency import currency_from_settings

        tenant = await self._db.get(Tenant, tenant_id)
        return currency_from_settings(tenant.settings_json if tenant is not None else None)

    def resolve_currency(self, requested: str | None, tenant_currency: str) -> str:
        """Financial records must use the tenant currency; a mismatch is rejected."""
        if requested is None or not str(requested).strip():
            return tenant_currency
        normalized = normalize_currency(requested)
        if normalized is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Currency must be a three-letter ISO-4217 code",
            )
        if normalized != tenant_currency:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Currency {normalized} does not match the organization currency "
                    f"{tenant_currency}"
                ),
            )
        return tenant_currency

    async def sync_contribution_totals(self, tenant_id, contribution):
        """Recompute paid amount, balance and status from the payment ledger."""
        from app.modules.finance.ledger import as_decimal, derive_contribution_status

        paid = await self._repo.sum_active_payments(tenant_id, contribution.id)
        expected = as_decimal(contribution.expected_amount)
        new_status = derive_contribution_status(
            expected=expected,
            paid=paid,
            due_date=contribution.due_date,
            waived=contribution.status == "waived",
        )
        return await self._repo.update_contribution(
            tenant_id,
            contribution.id,
            {"paid_amount": paid, "balance": expected - paid, "status": new_status},
        )

    async def ensure_year_open(self, tenant_id, year: int) -> None:
        """Refuse any financial write inside a closed exercise."""
        period = await self._repo.get_finance_period(tenant_id, year)
        if period is not None and period.status == "closed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Exercise {year} is closed. Reopen it before recording any change."
                ),
            )

    async def resolve_account_id(self, tenant_id, requested_account_id, payment_method: str):
        """Resolve the treasury account for a financial entry (implemented by TreasuryMixin)."""
        raise NotImplementedError

    async def next_receipt_number(self, tenant_id, year: int) -> str:
        """Allocate a receipt number (implemented by ContributionRecordsMixin)."""
        raise NotImplementedError

    async def expense_category_codes(
        self, tenant_id, *, commit: bool = False
    ) -> list[str]:
        """Return the tenant expense category codes (implemented by CategoriesMixin)."""
        raise NotImplementedError

    async def segregation_required(self, tenant_id) -> bool:
        """True when the tenant requires a different user to validate a receipt."""
        import json

        tenant = await self._db.get(Tenant, tenant_id)
        if tenant is None or not isinstance(tenant.settings_json, str):
            return False
        try:
            settings_raw = json.loads(tenant.settings_json)
        except json.JSONDecodeError:
            return False
        finance = settings_raw.get("finance", {}) if isinstance(settings_raw, dict) else {}
        if not isinstance(finance, dict):
            return False
        return bool(finance.get("require_separate_receipt_validator", False))

    def with_notification_providers(self, providers: list[NotificationProvider]) -> Self:
        self._notification_providers = providers
        self._events.with_notification_providers(providers)
        return self
