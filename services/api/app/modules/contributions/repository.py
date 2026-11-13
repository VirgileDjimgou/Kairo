from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.contributions.models import (
    ContributionReceiptDeclaration,
    ContributionRecord,
    ContributionReminder,
    ExpenseRecord,
    FinanceAccount,
    FinanceBudgetLine,
    FinanceExpenseCategory,
    FinanceOpeningBalance,
    FinancePeriod,
    FinanceReceiptCounter,
    PaymentRecord,
)


def _normalize_decimal(value: Decimal) -> Decimal:
    """Round Decimal to 2 places and strip excess trailing zeros."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class ContributionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_contribution(
        self, tenant_id: UUID, data: dict
    ) -> ContributionRecord:
        data["tenant_id"] = tenant_id
        data["balance"] = Decimal(str(data.get("expected_amount", 0))) - Decimal(str(data.get("paid_amount", 0)))
        record = ContributionRecord(**data)
        self._db.add(record)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def get_contribution(
        self, tenant_id: UUID, contribution_id: UUID
    ) -> ContributionRecord | None:
        result = await self._db.execute(
            select(ContributionRecord).where(
                ContributionRecord.tenant_id == tenant_id,
                ContributionRecord.id == contribution_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_contribution_by_member_year(
        self, tenant_id: UUID, profile_id: UUID, year: int
    ) -> ContributionRecord | None:
        result = await self._db.execute(
            select(ContributionRecord).where(
                ContributionRecord.tenant_id == tenant_id,
                ContributionRecord.membership_profile_id == profile_id,
                ContributionRecord.year == year,
            )
        )
        return result.scalars().first()

    async def list_by_profile(
        self, tenant_id: UUID, profile_id: UUID
    ) -> list[ContributionRecord]:
        result = await self._db.execute(
            select(ContributionRecord).where(
                ContributionRecord.tenant_id == tenant_id,
                ContributionRecord.membership_profile_id == profile_id,
            ).order_by(ContributionRecord.year.desc())
        )
        return list(result.scalars().all())

    async def list_by_tenant(
        self, tenant_id: UUID, year: int | None = None
    ) -> list[ContributionRecord]:
        query = select(ContributionRecord).where(
            ContributionRecord.tenant_id == tenant_id
        )
        if year:
            query = query.where(ContributionRecord.year == year)
        query = query.order_by(ContributionRecord.year.desc())
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def update_contribution(
        self, tenant_id: UUID, contribution_id: UUID, data: dict
    ) -> ContributionRecord | None:
        record = await self.get_contribution(tenant_id, contribution_id)
        if not record:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(record, key, value)
        record.balance = record.expected_amount - record.paid_amount
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def delete_contribution(self, tenant_id: UUID, contribution_id: UUID) -> bool:
        record = await self.get_contribution(tenant_id, contribution_id)
        if not record:
            return False
        await self._db.delete(record)
        await self._db.flush()
        return True

    async def create_payment(self, tenant_id: UUID, data: dict) -> PaymentRecord:
        data["tenant_id"] = tenant_id
        record = PaymentRecord(**data)
        self._db.add(record)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def get_payment(
        self, tenant_id: UUID, payment_id: UUID
    ) -> PaymentRecord | None:
        result = await self._db.execute(
            select(PaymentRecord).where(
                PaymentRecord.tenant_id == tenant_id,
                PaymentRecord.id == payment_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_payments_by_contribution(
        self, tenant_id: UUID, contribution_id: UUID
    ) -> list[PaymentRecord]:
        result = await self._db.execute(
            select(PaymentRecord).where(
                PaymentRecord.tenant_id == tenant_id,
                PaymentRecord.contribution_record_id == contribution_id,
            ).order_by(PaymentRecord.paid_at.desc())
        )
        return list(result.scalars().all())

    async def list_payments_by_tenant(
        self, tenant_id: UUID
    ) -> list[PaymentRecord]:
        result = await self._db.execute(
            select(PaymentRecord).where(
                PaymentRecord.tenant_id == tenant_id
            ).order_by(PaymentRecord.paid_at.desc())
        )
        return list(result.scalars().all())

    async def get_payment_by_idempotency_key(
        self, tenant_id: UUID, idempotency_key: str
    ) -> PaymentRecord | None:
        result = await self._db.execute(
            select(PaymentRecord).where(
                PaymentRecord.tenant_id == tenant_id,
                PaymentRecord.idempotency_key == idempotency_key,
            )
        )
        return result.scalar_one_or_none()

    async def count_payments(self, tenant_id: UUID, contribution_id: UUID) -> int:
        result = await self._db.execute(
            select(func.count(PaymentRecord.id)).where(
                PaymentRecord.tenant_id == tenant_id,
                PaymentRecord.contribution_record_id == contribution_id,
            )
        )
        return int(result.scalar_one())

    async def sum_active_payments(
        self, tenant_id: UUID, contribution_id: UUID
    ) -> Decimal:
        """Sum every payment that has not been reversed."""
        result = await self._db.execute(
            select(func.coalesce(func.sum(PaymentRecord.amount), 0)).where(
                PaymentRecord.tenant_id == tenant_id,
                PaymentRecord.contribution_record_id == contribution_id,
                PaymentRecord.reversed_at.is_(None),
            )
        )
        return _normalize_decimal(Decimal(str(result.scalar_one())))

    async def lock_contribution(
        self, tenant_id: UUID, contribution_id: UUID
    ) -> ContributionRecord | None:
        """Load a contribution row with a write lock on supporting databases."""
        result = await self._db.execute(
            select(ContributionRecord)
            .where(
                ContributionRecord.tenant_id == tenant_id,
                ContributionRecord.id == contribution_id,
            )
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def update_payment(
        self, tenant_id: UUID, payment_id: UUID, data: dict
    ) -> PaymentRecord | None:
        record = await self.get_payment(tenant_id, payment_id)
        if not record:
            return None
        for key, value in data.items():
            setattr(record, key, value)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def count_receipt_declarations_for_contribution(
        self, tenant_id: UUID, contribution_id: UUID
    ) -> int:
        result = await self._db.execute(
            select(func.count(ContributionReceiptDeclaration.id)).where(
                ContributionReceiptDeclaration.tenant_id == tenant_id,
                ContributionReceiptDeclaration.contribution_record_id == contribution_id,
            )
        )
        return int(result.scalar_one())

    async def delete_payment(self, tenant_id: UUID, payment_id: UUID) -> bool:
        record = await self.get_payment(tenant_id, payment_id)
        if not record:
            return False
        await self._db.delete(record)
        await self._db.flush()
        return True

    async def create_expense(self, tenant_id: UUID, data: dict) -> ExpenseRecord:
        data["tenant_id"] = tenant_id
        record = ExpenseRecord(**data)
        self._db.add(record)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def list_expenses_by_tenant(
        self,
        tenant_id: UUID,
        *,
        year: int | None = None,
        category: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[ExpenseRecord]:
        query = select(ExpenseRecord).where(ExpenseRecord.tenant_id == tenant_id)
        if year is not None:
            # A portable half-open interval works with both PostgreSQL and SQLite.
            from datetime import UTC, datetime

            query = query.where(
                ExpenseRecord.spent_at >= datetime(year, 1, 1, tzinfo=UTC),
                ExpenseRecord.spent_at < datetime(year + 1, 1, 1, tzinfo=UTC),
            )
        if category is not None:
            query = query.where(ExpenseRecord.category == category)
        query = query.order_by(ExpenseRecord.spent_at.desc(), ExpenseRecord.created_at.desc())
        if offset:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def get_expense(
        self, tenant_id: UUID, expense_id: UUID
    ) -> ExpenseRecord | None:
        result = await self._db.execute(
            select(ExpenseRecord).where(
                ExpenseRecord.tenant_id == tenant_id,
                ExpenseRecord.id == expense_id,
            )
        )
        return result.scalar_one_or_none()

    async def update_expense_attachment(
        self, tenant_id: UUID, expense_id: UUID, data: dict
    ) -> ExpenseRecord | None:
        record = await self.get_expense(tenant_id, expense_id)
        if record is None:
            return None
        for key, value in data.items():
            setattr(record, key, value)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def update_expense(
        self, tenant_id: UUID, expense_id: UUID, data: dict
    ) -> ExpenseRecord | None:
        return await self.update_expense_attachment(tenant_id, expense_id, data)

    async def get_finance_period(
        self, tenant_id: UUID, year: int
    ) -> FinancePeriod | None:
        result = await self._db.execute(
            select(FinancePeriod).where(
                FinancePeriod.tenant_id == tenant_id,
                FinancePeriod.year == year,
            )
        )
        return result.scalar_one_or_none()

    async def list_finance_periods(self, tenant_id: UUID) -> list[FinancePeriod]:
        result = await self._db.execute(
            select(FinancePeriod)
            .where(FinancePeriod.tenant_id == tenant_id)
            .order_by(FinancePeriod.year.desc())
        )
        return list(result.scalars().all())

    async def upsert_finance_period(
        self, tenant_id: UUID, year: int, data: dict
    ) -> FinancePeriod:
        record = await self.get_finance_period(tenant_id, year)
        if record is None:
            record = FinancePeriod(tenant_id=tenant_id, year=year, **data)
            self._db.add(record)
        else:
            for key, value in data.items():
                setattr(record, key, value)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def increment_receipt_counter(self, tenant_id: UUID, year: int) -> int:
        result = await self._db.execute(
            select(FinanceReceiptCounter)
            .where(
                FinanceReceiptCounter.tenant_id == tenant_id,
                FinanceReceiptCounter.year == year,
            )
            .with_for_update()
        )
        counter = result.scalar_one_or_none()
        if counter is None:
            counter = FinanceReceiptCounter(
                tenant_id=tenant_id, year=year, last_number=0
            )
            self._db.add(counter)
        counter.last_number += 1
        await self._db.flush()
        await self._db.refresh(counter)
        return int(counter.last_number)

    async def list_finance_accounts(self, tenant_id: UUID) -> list[FinanceAccount]:
        result = await self._db.execute(
            select(FinanceAccount)
            .where(FinanceAccount.tenant_id == tenant_id)
            .order_by(FinanceAccount.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_finance_account(
        self, tenant_id: UUID, account_id: UUID
    ) -> FinanceAccount | None:
        result = await self._db.execute(
            select(FinanceAccount).where(
                FinanceAccount.tenant_id == tenant_id,
                FinanceAccount.id == account_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_finance_account(
        self, tenant_id: UUID, *, name: str, kind: str, is_default: bool = False
    ) -> FinanceAccount:
        record = FinanceAccount(
            tenant_id=tenant_id, name=name, kind=kind, is_default=is_default
        )
        self._db.add(record)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def list_opening_balances(
        self, tenant_id: UUID, year: int
    ) -> list[FinanceOpeningBalance]:
        result = await self._db.execute(
            select(FinanceOpeningBalance).where(
                FinanceOpeningBalance.tenant_id == tenant_id,
                FinanceOpeningBalance.year == year,
            )
        )
        return list(result.scalars().all())

    async def list_opening_balances_up_to(
        self, tenant_id: UUID, year: int
    ) -> list[FinanceOpeningBalance]:
        result = await self._db.execute(
            select(FinanceOpeningBalance).where(
                FinanceOpeningBalance.tenant_id == tenant_id,
                FinanceOpeningBalance.year <= year,
            )
        )
        return list(result.scalars().all())

    async def upsert_opening_balance(
        self,
        tenant_id: UUID,
        account_id: UUID,
        year: int,
        *,
        amount,
        currency: str,
    ) -> FinanceOpeningBalance:
        result = await self._db.execute(
            select(FinanceOpeningBalance).where(
                FinanceOpeningBalance.tenant_id == tenant_id,
                FinanceOpeningBalance.account_id == account_id,
                FinanceOpeningBalance.year == year,
            )
        )
        record = result.scalar_one_or_none()
        if record is None:
            record = FinanceOpeningBalance(
                tenant_id=tenant_id,
                account_id=account_id,
                year=year,
                amount=amount,
                currency=currency,
            )
            self._db.add(record)
        else:
            record.amount = amount
            record.currency = currency
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def list_payments_before_year(
        self, tenant_id: UUID, year: int
    ) -> list[PaymentRecord]:
        from datetime import UTC, datetime

        result = await self._db.execute(
            select(PaymentRecord).where(
                PaymentRecord.tenant_id == tenant_id,
                PaymentRecord.reversed_at.is_(None),
                PaymentRecord.paid_at < datetime(year, 1, 1, tzinfo=UTC),
            )
        )
        return list(result.scalars().all())

    async def list_expenses_before_year(
        self, tenant_id: UUID, year: int
    ) -> list[ExpenseRecord]:
        from datetime import UTC, datetime

        result = await self._db.execute(
            select(ExpenseRecord).where(
                ExpenseRecord.tenant_id == tenant_id,
                ExpenseRecord.spent_at < datetime(year, 1, 1, tzinfo=UTC),
            )
        )
        return list(result.scalars().all())

    async def list_expense_categories(
        self, tenant_id: UUID
    ) -> list[FinanceExpenseCategory]:
        result = await self._db.execute(
            select(FinanceExpenseCategory)
            .where(FinanceExpenseCategory.tenant_id == tenant_id)
            .order_by(FinanceExpenseCategory.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_expense_category_by_code(
        self, tenant_id: UUID, code: str
    ) -> FinanceExpenseCategory | None:
        result = await self._db.execute(
            select(FinanceExpenseCategory).where(
                FinanceExpenseCategory.tenant_id == tenant_id,
                FinanceExpenseCategory.code == code,
            )
        )
        return result.scalar_one_or_none()

    async def create_expense_category(
        self,
        tenant_id: UUID,
        *,
        code: str,
        name: str,
        is_default: bool = False,
    ) -> FinanceExpenseCategory:
        record = FinanceExpenseCategory(
            tenant_id=tenant_id, code=code, name=name, is_default=is_default
        )
        self._db.add(record)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def list_budget_lines(
        self, tenant_id: UUID, year: int
    ) -> list[FinanceBudgetLine]:
        result = await self._db.execute(
            select(FinanceBudgetLine)
            .where(
                FinanceBudgetLine.tenant_id == tenant_id,
                FinanceBudgetLine.year == year,
            )
            .order_by(FinanceBudgetLine.direction.asc(), FinanceBudgetLine.category.asc())
        )
        return list(result.scalars().all())

    async def replace_budget_lines(
        self, tenant_id: UUID, year: int, lines: list[dict]
    ) -> list[FinanceBudgetLine]:
        await self._db.execute(
            delete(FinanceBudgetLine).where(
                FinanceBudgetLine.tenant_id == tenant_id,
                FinanceBudgetLine.year == year,
            )
        )
        created: list[FinanceBudgetLine] = []
        for line in lines:
            record = FinanceBudgetLine(tenant_id=tenant_id, year=year, **line)
            self._db.add(record)
            created.append(record)
        await self._db.flush()
        for record in created:
            await self._db.refresh(record)
        return created

    async def create_receipt_declaration(
        self, tenant_id: UUID, data: dict
    ) -> ContributionReceiptDeclaration:
        data["tenant_id"] = tenant_id
        record = ContributionReceiptDeclaration(**data)
        self._db.add(record)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def get_receipt_declaration(
        self, tenant_id: UUID, declaration_id: UUID
    ) -> ContributionReceiptDeclaration | None:
        result = await self._db.execute(select(ContributionReceiptDeclaration).where(
            ContributionReceiptDeclaration.tenant_id == tenant_id,
            ContributionReceiptDeclaration.id == declaration_id,
        ))
        return result.scalar_one_or_none()

    async def list_receipt_declarations(
        self, tenant_id: UUID, *, declarant_user_id: UUID | None = None,
        membership_profile_id: UUID | None = None,
    ) -> list[ContributionReceiptDeclaration]:
        query = select(ContributionReceiptDeclaration).where(
            ContributionReceiptDeclaration.tenant_id == tenant_id
        )
        if declarant_user_id is not None:
            query = query.where(ContributionReceiptDeclaration.declarant_user_id == declarant_user_id)
        if membership_profile_id is not None:
            query = query.where(ContributionReceiptDeclaration.membership_profile_id == membership_profile_id)
        result = await self._db.execute(query.order_by(ContributionReceiptDeclaration.created_at.desc()))
        return list(result.scalars().all())

    async def update_receipt_declaration(
        self, tenant_id: UUID, declaration_id: UUID, data: dict
    ) -> ContributionReceiptDeclaration | None:
        record = await self.get_receipt_declaration(tenant_id, declaration_id)
        if record is None:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(record, key, value)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def create_reminder(self, tenant_id: UUID, data: dict) -> ContributionReminder:
        data["tenant_id"] = tenant_id
        record = ContributionReminder(**data)
        self._db.add(record)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def list_reminders_by_tenant(
        self,
        tenant_id: UUID,
        *,
        year: int | None = None,
        profile_id: UUID | None = None,
        limit: int = 50,
    ) -> list[ContributionReminder]:
        query = select(ContributionReminder).where(
            ContributionReminder.tenant_id == tenant_id
        )
        if profile_id is not None:
            query = query.where(ContributionReminder.membership_profile_id == profile_id)
        if year is not None:
            query = query.join(
                ContributionRecord,
                ContributionRecord.id == ContributionReminder.contribution_record_id,
            ).where(ContributionRecord.year == year)
        query = query.order_by(
            ContributionReminder.sent_at.desc(),
            ContributionReminder.created_at.desc(),
        ).limit(limit)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def get_tenant_contribution_summary(
        self, tenant_id: UUID, year: int | None = None
    ) -> dict:
        query = select(
            func.count(ContributionRecord.id),
            func.coalesce(func.sum(ContributionRecord.expected_amount), 0),
            func.coalesce(func.sum(ContributionRecord.paid_amount), 0),
            func.coalesce(func.sum(ContributionRecord.balance), 0),
        ).where(ContributionRecord.tenant_id == tenant_id)
        if year:
            query = query.where(ContributionRecord.year == year)
        result = await self._db.execute(query)
        row = result.one()
        return {
            "total_count": row[0],
            "total_expected": str(_normalize_decimal(Decimal(str(row[1])))),
            "total_paid": str(_normalize_decimal(Decimal(str(row[2])))),
            "total_balance": str(_normalize_decimal(Decimal(str(row[3])))),
        }
