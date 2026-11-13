from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.contributions.models import (
    ContributionReceiptStatus,
    FinancialIncomeType,
)
from app.modules.contributions.schemas import (
    AnnualBudgetResponse,
    BudgetCategoryTotal,
    BudgetPlanLine,
    BudgetPlanResponse,
    BudgetPlanUpdate,
    ExpenseRecordResponse,
)
from app.modules.finance.base import FinanceServiceBase
from app.modules.finance.ledger import as_decimal


class BudgetingMixin(FinanceServiceBase):
    @staticmethod
    def _income_categories() -> list[str]:
        return [category.value for category in FinancialIncomeType]

    async def get_annual_budget(
        self, tenant_id: UUID, *, year: int
    ) -> AnnualBudgetResponse:
        """Return realized annual flows, the voted plan and their variance."""
        tenant_currency = await self.tenant_currency(tenant_id)
        mixed_currencies: set[str] = set()
        income_categories = self._income_categories()
        expense_categories = await self.expense_category_codes(tenant_id, commit=True)
        income_totals = {category: Decimal("0.00") for category in income_categories}
        expense_totals = {category: Decimal("0.00") for category in expense_categories}

        for payment in await self._repo.list_payments_by_tenant(tenant_id):
            if payment.paid_at.year == year and payment.reversed_at is None:
                if payment.currency != tenant_currency:
                    mixed_currencies.add(payment.currency)
                income_totals[FinancialIncomeType.membership_contribution.value] += payment.amount

        # Non-membership receipts do not create PaymentRecord rows. Include the
        # amounts only after the treasurer has accepted them to avoid counting
        # a declaration and an official payment twice.
        receipts = await self._repo.list_receipt_declarations(tenant_id)
        accepted_statuses = {
            ContributionReceiptStatus.validated.value,
            ContributionReceiptStatus.partially_validated.value,
        }
        for receipt in receipts:
            if (
                receipt.status in accepted_statuses
                and receipt.processed_at is not None
                and receipt.received_at.year == year
                and receipt.income_type != FinancialIncomeType.membership_contribution.value
            ):
                if receipt.currency != tenant_currency:
                    mixed_currencies.add(receipt.currency)
                income_totals[receipt.income_type] = income_totals.get(
                    receipt.income_type, Decimal("0.00")
                ) + (receipt.processed_amount or receipt.amount)

        expenses = await self._repo.list_expenses_by_tenant(tenant_id, year=year)
        for expense in expenses:
            if expense.reversed_at is not None or expense.status == "rejected":
                continue
            if expense.currency != tenant_currency:
                mixed_currencies.add(expense.currency)
            expense_totals[expense.category] = expense_totals.get(
                expense.category, Decimal("0.00")
            ) + expense.amount

        if mixed_currencies:
            currencies = ", ".join(sorted(mixed_currencies))
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Finance records exist in {currencies} while the organization "
                    f"currency is {tenant_currency}. Normalize the ledger before "
                    "producing a budget."
                ),
            )

        planned_income: dict[str, Decimal] = {}
        planned_expense: dict[str, Decimal] = {}
        for line in await self._repo.list_budget_lines(tenant_id, year):
            amount = as_decimal(line.planned_amount)
            if line.direction == "income":
                planned_income[line.category] = amount
            elif line.direction == "expense":
                planned_expense[line.category] = amount

        income_total = sum(income_totals.values(), Decimal("0.00"))
        expense_total = sum(expense_totals.values(), Decimal("0.00"))
        planned_income_total = sum(planned_income.values(), Decimal("0.00"))
        planned_expense_total = sum(planned_expense.values(), Decimal("0.00"))

        return AnnualBudgetResponse(
            year=year,
            currency=tenant_currency,
            income_total=income_total,
            expense_total=expense_total,
            available_balance=income_total - expense_total,
            planned_income_total=planned_income_total,
            planned_expense_total=planned_expense_total,
            income_variance=income_total - planned_income_total,
            expense_variance=expense_total - planned_expense_total,
            income_by_category=[
                BudgetCategoryTotal(
                    category=category,
                    amount=income_totals[category],
                    planned_amount=planned_income.get(category, Decimal("0.00")),
                    variance=income_totals[category]
                    - planned_income.get(category, Decimal("0.00")),
                )
                for category in income_categories
            ],
            expenses_by_category=[
                BudgetCategoryTotal(
                    category=category,
                    amount=expense_totals[category],
                    planned_amount=planned_expense.get(category, Decimal("0.00")),
                    variance=expense_totals[category]
                    - planned_expense.get(category, Decimal("0.00")),
                )
                for category in expense_categories
            ],
            recent_expenses=[
                ExpenseRecordResponse.model_validate(expense) for expense in expenses[:6]
            ],
        )

    async def get_budget_plan(
        self, tenant_id: UUID, *, year: int
    ) -> BudgetPlanResponse:
        currency = await self.tenant_currency(tenant_id)
        stored = {
            (line.direction, line.category): as_decimal(line.planned_amount)
            for line in await self._repo.list_budget_lines(tenant_id, year)
        }
        expense_categories = await self.expense_category_codes(tenant_id, commit=True)
        lines = [
            BudgetPlanLine(
                direction="income",
                category=category,
                planned_amount=stored.get(("income", category), Decimal("0.00")),
            )
            for category in self._income_categories()
        ] + [
            BudgetPlanLine(
                direction="expense",
                category=category,
                planned_amount=stored.get(("expense", category), Decimal("0.00")),
            )
            for category in expense_categories
        ]
        return BudgetPlanResponse(
            year=year,
            currency=currency,
            lines=lines,
            planned_income_total=sum(
                (line.planned_amount for line in lines if line.direction == "income"),
                Decimal("0.00"),
            ),
            planned_expense_total=sum(
                (line.planned_amount for line in lines if line.direction == "expense"),
                Decimal("0.00"),
            ),
        )

    async def set_budget_plan(
        self,
        tenant_id: UUID,
        year: int,
        data: BudgetPlanUpdate,
        *,
        actor_user_id: UUID,
    ) -> BudgetPlanResponse:
        await self.ensure_year_open(tenant_id, year)
        currency = await self.tenant_currency(tenant_id)
        income_categories = set(self._income_categories())
        expense_categories = set(await self.expense_category_codes(tenant_id, commit=True))

        seen: set[tuple[str, str]] = set()
        lines: list[dict] = []
        for line in data.lines:
            key = (line.direction, line.category)
            if key in seen:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Duplicate budget line {line.direction}/{line.category}",
                )
            seen.add(key)
            allowed = income_categories if line.direction == "income" else expense_categories
            if line.category not in allowed:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        f"Unknown {line.direction} category '{line.category}'"
                    ),
                )
            lines.append(
                {
                    "direction": line.direction,
                    "category": line.category,
                    "planned_amount": as_decimal(line.planned_amount),
                    "currency": currency,
                }
            )

        await self._repo.replace_budget_lines(tenant_id, year, lines)
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="budget_plan_updated",
            entity_type="finance_budget",
            entity_id=None,
            module_key="contributions",
            details={
                "year": year,
                "line_count": len(lines),
                "planned_income_total": str(
                    sum(
                        (entry["planned_amount"] for entry in lines if entry["direction"] == "income"),
                        Decimal("0.00"),
                    )
                ),
                "planned_expense_total": str(
                    sum(
                        (entry["planned_amount"] for entry in lines if entry["direction"] == "expense"),
                        Decimal("0.00"),
                    )
                ),
            },
        )
        await self._db.commit()
        return await self.get_budget_plan(tenant_id, year=year)
