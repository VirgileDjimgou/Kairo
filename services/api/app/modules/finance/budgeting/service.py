from decimal import Decimal
from uuid import UUID

from app.modules.contributions.models import (
    ContributionReceiptStatus,
    ExpenseCategory,
    FinancialIncomeType,
)
from app.modules.contributions.schemas import (
    AnnualBudgetResponse,
    BudgetCategoryTotal,
    ExpenseRecordResponse,
)
from app.modules.finance.base import FinanceServiceBase


class BudgetingMixin(FinanceServiceBase):
    async def get_annual_budget(
        self, tenant_id: UUID, *, year: int
    ) -> AnnualBudgetResponse:
        """Return realized annual inflows, outflows and remaining treasury balance."""
        income_categories = [
            FinancialIncomeType.membership_contribution.value,
            FinancialIncomeType.donation.value,
            FinancialIncomeType.sponsorship.value,
            FinancialIncomeType.tournament_proceeds.value,
            FinancialIncomeType.disciplinary_payment.value,
            FinancialIncomeType.other_income.value,
        ]
        expense_categories = [category.value for category in ExpenseCategory]
        income_totals = {category: Decimal("0.00") for category in income_categories}
        expense_totals = {category: Decimal("0.00") for category in expense_categories}

        for payment in await self._repo.list_payments_by_tenant(tenant_id):
            if payment.paid_at.year == year:
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
                and receipt.processed_at.year == year
                and receipt.income_type != FinancialIncomeType.membership_contribution.value
            ):
                income_totals[receipt.income_type] = income_totals.get(
                    receipt.income_type, Decimal("0.00")
                ) + (receipt.processed_amount or receipt.amount)

        expenses = await self._repo.list_expenses_by_tenant(tenant_id, year=year)
        for expense in expenses:
            expense_totals[expense.category] = expense_totals.get(
                expense.category, Decimal("0.00")
            ) + expense.amount

        income_total = sum(income_totals.values(), Decimal("0.00"))
        expense_total = sum(expense_totals.values(), Decimal("0.00"))
        return AnnualBudgetResponse(
            year=year,
            income_total=income_total,
            expense_total=expense_total,
            available_balance=income_total - expense_total,
            income_by_category=[
                BudgetCategoryTotal(category=category, amount=income_totals[category])
                for category in income_categories
            ],
            expenses_by_category=[
                BudgetCategoryTotal(category=category, amount=expense_totals[category])
                for category in expense_categories
            ],
            recent_expenses=[
                ExpenseRecordResponse.model_validate(expense) for expense in expenses[:6]
            ],
        )
