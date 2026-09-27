from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.service import AuditService
from app.providers.notifications.base import (
    NotificationProvider,
)


@dataclass(slots=True)
class _RawNotificationAuditEvent:
    id: object
    action: str
    entity_id: str | None
    details: dict[str, object]
    created_at: datetime


class NotificationServiceBase:
    STALE_PENDING_AFTER = timedelta(minutes=30)

    def __init__(
        self,
        providers: list[NotificationProvider],
        db: AsyncSession | None = None,
        audit: AuditService | None = None,
    ) -> None:
        self._providers = providers
        self._provider_map = {provider.channel: provider for provider in providers}
        self._db = db
        self._audit: AuditService | None = audit
