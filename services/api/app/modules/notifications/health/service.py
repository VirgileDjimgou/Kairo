from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select

from app.core.config import settings
from app.modules.notifications.user_base import UserNotificationServiceBase
from app.modules.notifications.user_models import (
    FirebasePushSubscription,
    NotificationOutboxEvent,
    WebPushSubscription,
)
from app.modules.notifications.user_schemas import NotificationHealthResponse

WORKER_STALE_AFTER_SECONDS = 300


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


class HealthMixin(UserNotificationServiceBase):
    """Operator-facing notification health. Never exposes keys or tokens."""

    async def health(self, tenant_id: UUID) -> NotificationHealthResponse:
        now = datetime.now(UTC)
        pending = int(
            await self._db.scalar(
                select(func.count(NotificationOutboxEvent.id)).where(
                    NotificationOutboxEvent.tenant_id == tenant_id,
                    NotificationOutboxEvent.status == "pending",
                )
            )
            or 0
        )
        failed = int(
            await self._db.scalar(
                select(func.count(NotificationOutboxEvent.id)).where(
                    NotificationOutboxEvent.tenant_id == tenant_id,
                    NotificationOutboxEvent.status == "failed",
                )
            )
            or 0
        )
        oldest_pending_at = _as_utc(
            await self._db.scalar(
                select(func.min(NotificationOutboxEvent.created_at)).where(
                    NotificationOutboxEvent.tenant_id == tenant_id,
                    NotificationOutboxEvent.status == "pending",
                )
            )
        )
        last_completed_at = _as_utc(
            await self._db.scalar(
                select(func.max(NotificationOutboxEvent.processed_at)).where(
                    NotificationOutboxEvent.tenant_id == tenant_id,
                )
            )
        )
        disabled_web = int(
            await self._db.scalar(
                select(func.count(WebPushSubscription.id)).where(
                    WebPushSubscription.tenant_id == tenant_id,
                    WebPushSubscription.disabled_at.is_not(None),
                )
            )
            or 0
        )
        disabled_fcm = int(
            await self._db.scalar(
                select(func.count(FirebasePushSubscription.id)).where(
                    FirebasePushSubscription.tenant_id == tenant_id,
                    FirebasePushSubscription.disabled_at.is_not(None),
                )
            )
            or 0
        )

        worker_running = True
        if pending > 0:
            fresh_completion = (
                last_completed_at is not None
                and (now - last_completed_at).total_seconds() <= WORKER_STALE_AFTER_SECONDS
            )
            fresh_event = (
                oldest_pending_at is not None
                and (now - oldest_pending_at).total_seconds() <= WORKER_STALE_AFTER_SECONDS
            )
            worker_running = fresh_completion or fresh_event

        return NotificationHealthResponse(
            web_push_configured=bool(
                settings.web_push_enabled
                and settings.web_push_vapid_public_key
                and settings.web_push_vapid_private_key
            ),
            firebase_configured=bool(
                settings.firebase_messaging_enabled
                and settings.firebase_service_account_path
            ),
            worker_running=worker_running,
            pending_outbox=pending,
            failed_outbox=failed,
            oldest_pending_seconds=(
                int((now - oldest_pending_at).total_seconds())
                if oldest_pending_at is not None
                else None
            ),
            disabled_web_subscriptions=disabled_web,
            disabled_fcm_tokens=disabled_fcm,
            last_successful_dispatch_at=last_completed_at,
        )
