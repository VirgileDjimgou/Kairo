from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.service import AuditService
from app.modules.contributions.repository import ContributionRepository
from app.modules.domain_events.service import DomainEventService
from app.providers.notifications.base import NotificationProvider


class FinanceServiceBase:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = ContributionRepository(db)
        self._audit = AuditService(db)
        self._events = DomainEventService(db)
        self._notification_providers: list[NotificationProvider] = []

    def with_notification_providers(self, providers: list[NotificationProvider]) -> Self:
        self._notification_providers = providers
        self._events.with_notification_providers(providers)
        return self
