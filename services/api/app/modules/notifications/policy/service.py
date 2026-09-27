from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import select

from app.modules.notifications.user_base import UserNotificationServiceBase
from app.modules.notifications.user_models import NotificationOutboxEvent


class PolicyMixin(UserNotificationServiceBase):
    """Canonical notification policy and recipient resolver.

    Every producer submits a notification intent here. This is the only place that
    writes recipient outbox events, so the canonical envelope, idempotency and the
    sensitive-push policy stay consistent across modules and clients.
    """

    async def notify(
        self,
        *,
        tenant_id: UUID,
        event_type: str,
        recipients: Iterable[UUID],
        category: str,
        target_path: str,
        deduplication_key: str,
        metadata: dict[str, object] | None = None,
        priority: str = "normal",
        event_id: UUID | None = None,
        correlation_id: str | None = None,
        push_policy: str = "generic",
    ) -> bool:
        recipient_ids = sorted({user_id for user_id in recipients})
        if not recipient_ids:
            return False
        existing = await self._db.scalar(
            select(NotificationOutboxEvent.id).where(
                NotificationOutboxEvent.tenant_id == tenant_id,
                NotificationOutboxEvent.deduplication_key == deduplication_key,
            )
        )
        if existing is not None:
            return False
        await self.enqueue(
            tenant_id=tenant_id,
            event_type=event_type,
            recipients=recipient_ids,
            category=category,
            target_path=target_path,
            deduplication_key=deduplication_key,
            metadata=metadata,
            priority=priority,
            event_id=event_id,
            correlation_id=correlation_id,
            push_policy=push_policy,
        )
        return True
