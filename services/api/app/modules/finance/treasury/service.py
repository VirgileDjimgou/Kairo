"""Treasury accounts, opening balances and the consolidated cash position."""

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.contributions.schemas import (
    FinanceAccountResponse,
    TreasuryPositionAccount,
    TreasuryPositionResponse,
)
from app.modules.finance.base import FinanceServiceBase
from app.modules.finance.ledger import as_decimal

DEFAULT_ACCOUNTS = (
    ("Caisse", "cash"),
    ("Banque", "bank"),
)
UNASSIGNED_LABEL = "Non affecte"
PAYMENT_METHOD_KIND = {
    "cash": "cash",
    "bank_transfer": "bank",
    "card": "bank",
    "check": "bank",
    "other": "cash",
}


class TreasuryMixin(FinanceServiceBase):
    async def ensure_default_accounts(self, tenant_id: UUID):
        """Create the cash and bank accounts on first use."""
        accounts = await self._repo.list_finance_accounts(tenant_id)
        if accounts:
            return accounts
        created = []
        for name, kind in DEFAULT_ACCOUNTS:
            created.append(
                await self._repo.create_finance_account(
                    tenant_id, name=name, kind=kind, is_default=True
                )
            )
        await self._db.flush()
        return created

    async def list_accounts(self, tenant_id: UUID) -> list[FinanceAccountResponse]:
        accounts = await self.ensure_default_accounts(tenant_id)
        # The default accounts are bootstrap data; persist them so a read does not
        # recreate them on every request.
        await self._db.commit()
        return [
            FinanceAccountResponse(
                id=account.id,
                name=account.name,
                kind=account.kind,
                is_default=account.is_default,
            )
            for account in accounts
        ]

    async def resolve_account_id(
        self, tenant_id: UUID, requested_account_id: UUID | None, payment_method: str
    ) -> UUID:
        accounts = await self.ensure_default_accounts(tenant_id)
        if requested_account_id is not None:
            for account in accounts:
                if account.id == requested_account_id:
                    return account.id
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Treasury account not found",
            )
        wanted_kind = PAYMENT_METHOD_KIND.get(payment_method, "cash")
        for account in accounts:
            if account.kind == wanted_kind:
                return account.id
        return accounts[0].id

    async def set_opening_balance(
        self,
        tenant_id: UUID,
        account_id: UUID,
        year: int,
        amount: Decimal,
        *,
        actor_user_id: UUID,
    ) -> TreasuryPositionResponse:
        await self.ensure_year_open(tenant_id, year)
        await self.ensure_default_accounts(tenant_id)
        account = await self._repo.get_finance_account(tenant_id, account_id)
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Treasury account not found",
            )
        currency = await self.tenant_currency(tenant_id)
        record = await self._repo.upsert_opening_balance(
            tenant_id,
            account_id,
            year,
            amount=as_decimal(amount),
            currency=currency,
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="opening_balance_set",
            entity_type="finance_opening_balance",
            entity_id=record.id,
            module_key="contributions",
            details={
                "account_id": str(account_id),
                "year": year,
                "amount": str(record.amount),
                "currency": record.currency,
            },
        )
        await self._db.commit()
        return await self.get_treasury_position(tenant_id, year)

    async def get_treasury_position(
        self, tenant_id: UUID, year: int
    ) -> TreasuryPositionResponse:
        await self.ensure_default_accounts(tenant_id)
        await self._db.commit()
        accounts = await self._repo.list_finance_accounts(tenant_id)
        currency = await self.tenant_currency(tenant_id)

        opening_records = await self._repo.list_opening_balances_up_to(tenant_id, year)
        declarations_by_payment = {
            declaration.payment_record_id: declaration
            for declaration in await self._repo.list_receipt_declarations(tenant_id)
            if declaration.payment_record_id is not None
        }
        all_payments = [
            payment
            for payment in await self._repo.list_payments_by_tenant(tenant_id)
            if payment.reversed_at is None
        ]
        all_expenses = [
            expense
            for expense in await self._repo.list_expenses_by_tenant(
                tenant_id, year=None, limit=None
            )
            if expense.reversed_at is None and expense.status != "rejected"
        ]

        def pending_custody(payment) -> Decimal:
            """Cash received by an office holder but not yet handed to the treasury."""
            if payment.payment_method != "cash":
                return Decimal("0.00")
            declaration = declarations_by_payment.get(payment.id)
            if declaration is None:
                return Decimal("0.00")
            if declaration.cash_handover_status in {None, "received_in_treasury"}:
                return Decimal("0.00")
            return as_decimal(payment.amount)

        for payment in all_payments:
            if payment.currency != currency:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"Treasury records exist in {payment.currency} while the "
                        f"organization currency is {currency}. Normalize the ledger "
                        "before computing the position."
                    ),
                )
        for expense in all_expenses:
            if expense.currency != currency:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"Treasury records exist in {expense.currency} while the "
                        f"organization currency is {currency}. Normalize the ledger "
                        "before computing the position."
                    ),
                )

        account_ids: list[UUID | None] = [account.id for account in accounts]
        if any(payment.account_id is None for payment in all_payments) or any(
            expense.account_id is None for expense in all_expenses
        ):
            account_ids.append(None)

        accounts_by_id = {account.id: account for account in accounts}
        rows: list[TreasuryPositionAccount] = []
        for account_id in account_ids:
            if account_id is None:
                name, kind = UNASSIGNED_LABEL, "other"
            else:
                account = accounts_by_id[account_id]
                name, kind = account.name, account.kind

            # An explicit opening balance is a reset: later years carry from that
            # baseline instead of re-adding the whole history.
            baselines = [
                record
                for record in opening_records
                if record.account_id == account_id and record.year <= year
            ]
            baseline = max(baselines, key=lambda record: record.year, default=None)
            opening = as_decimal(baseline.amount) if baseline is not None else Decimal("0.00")
            start_year = baseline.year if baseline is not None else None

            inflow = Decimal("0.00")
            outflow = Decimal("0.00")
            pending = Decimal("0.00")
            for payment in all_payments:
                if payment.account_id != account_id:
                    continue
                payment_year = payment.paid_at.year
                if payment_year == year:
                    inflow += as_decimal(payment.amount)
                    pending += pending_custody(payment)
                elif payment_year < year and (
                    start_year is None or payment_year >= start_year
                ):
                    opening += as_decimal(payment.amount)
                    opening -= pending_custody(payment)
            for expense in all_expenses:
                if expense.account_id != account_id:
                    continue
                expense_year = expense.spent_at.year
                if expense_year == year:
                    outflow += as_decimal(expense.amount)
                elif expense_year < year and (
                    start_year is None or expense_year >= start_year
                ):
                    opening -= as_decimal(expense.amount)

            rows.append(
                TreasuryPositionAccount(
                    account_id=account_id,
                    name=name,
                    kind=kind,
                    opening_balance=opening,
                    inflow=inflow,
                    outflow=outflow,
                    pending_custody=pending,
                    closing_balance=opening + inflow - outflow - pending,
                )
            )

        rows.sort(key=lambda row: (row.account_id is None, row.name))
        return TreasuryPositionResponse(
            year=year,
            currency=currency,
            accounts=rows,
            total_opening=sum((row.opening_balance for row in rows), Decimal("0.00")),
            total_inflow=sum((row.inflow for row in rows), Decimal("0.00")),
            total_outflow=sum((row.outflow for row in rows), Decimal("0.00")),
            total_pending_custody=sum(
                (row.pending_custody for row in rows), Decimal("0.00")
            ),
            total_closing=sum((row.closing_balance for row in rows), Decimal("0.00")),
        )
