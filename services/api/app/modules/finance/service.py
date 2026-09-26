from app.modules.finance.base import FinanceServiceBase
from app.modules.finance.budgeting.service import BudgetingMixin
from app.modules.finance.contributions.service import ContributionRecordsMixin
from app.modules.finance.custody.service import CustodyMixin
from app.modules.finance.expenses.service import ExpensesMixin
from app.modules.finance.receipts.service import ReceiptWorkflowMixin
from app.modules.finance.reminders.service import RemindersMixin
from app.modules.finance.reporting.service import FinanceExportRow, ReportingMixin


class ContributionService(
    ContributionRecordsMixin,
    ReceiptWorkflowMixin,
    CustodyMixin,
    ExpensesMixin,
    BudgetingMixin,
    RemindersMixin,
    ReportingMixin,
    FinanceServiceBase,
):
    """Facade composing the finance bounded-context domains.

    Public behaviour is unchanged: each command owns its transaction and the
    router keeps consuming this single entry point.
    """


__all__ = ["ContributionService", "FinanceExportRow"]
