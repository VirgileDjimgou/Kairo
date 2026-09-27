from app.modules.notifications.dispatch.service import DispatchMixin
from app.modules.notifications.history.service import HistoryMixin
from app.modules.notifications.reconciliation.service import ReconciliationMixin
from app.modules.notifications.service_base import NotificationServiceBase


class NotificationService(
    HistoryMixin,
    ReconciliationMixin,
    DispatchMixin,
    NotificationServiceBase,
):
    """Facade composing the notification domains (history, reconciliation, dispatch)."""
