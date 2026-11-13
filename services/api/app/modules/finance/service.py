from app.modules.finance.base import FinanceServiceBase
from app.modules.finance.budgeting.service import BudgetingMixin
from app.modules.finance.categories.service import CategoriesMixin
from app.modules.finance.contributions.service import ContributionRecordsMixin
from app.modules.finance.custody.service import CustodyMixin
from app.modules.finance.expenses.service import ExpensesMixin
from app.modules.finance.periods.service import PeriodsMixin
from app.modules.finance.receipts.service import ReceiptWorkflowMixin
from app.modules.finance.reminders.service import RemindersMixin
from app.modules.finance.reporting.service import FinanceExportRow, ReportingMixin
from app.modules.finance.treasury.service import TreasuryMixin


class ContributionService(
    ContributionRecordsMixin,
    ReceiptWorkflowMixin,
    CustodyMixin,
    ExpensesMixin,
    BudgetingMixin,
    CategoriesMixin,
    RemindersMixin,
    ReportingMixin,
    PeriodsMixin,
    TreasuryMixin,
    FinanceServiceBase,
):
    """Facade composing the finance bounded-context domains.

    Public behaviour is unchanged: each command owns its transaction and the
    router keeps consuming this single entry point.
    """


__all__ = ["ContributionService", "FinanceExportRow"]
