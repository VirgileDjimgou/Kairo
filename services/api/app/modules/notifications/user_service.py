from app.modules.notifications.devices.service import DevicesMixin
from app.modules.notifications.health.service import HealthMixin
from app.modules.notifications.inbox.service import InboxMixin
from app.modules.notifications.outbox.service import OutboxMixin
from app.modules.notifications.policy.service import PolicyMixin
from app.modules.notifications.preferences.service import PreferencesMixin
from app.modules.notifications.user_base import UserNotificationServiceBase


class UserNotificationService(
    InboxMixin,
    PolicyMixin,
    PreferencesMixin,
    DevicesMixin,
    HealthMixin,
    OutboxMixin,
    UserNotificationServiceBase,
):
    """Facade composing the notification domains (inbox, policy, preferences, devices, health, outbox)."""
