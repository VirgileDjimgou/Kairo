from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import func, select

from app.core.config import settings
from app.core.metrics import metrics
from app.modules.identity.models import User
from app.modules.notifications.user_base import UserNotificationServiceBase
from app.modules.notifications.user_models import (
    FirebasePushSubscription,
    NotificationDeviceProfile,
    NotificationOutboxEvent,
    UserNotification,
    WebPushSubscription,
)
from app.modules.notifications.user_schemas import (
    UnreachableNotificationRecipient,
)
from app.providers.push.base import (
    FirebasePushProvider,
    FirebasePushTarget,
    PushMessage,
    PushOutcome,
    WebPushProvider,
    WebPushTarget,
)

GENERIC_PUSH_TITLE = "Kairo"
GENERIC_PUSH_BODY = "Une nouvelle notification est disponible."
PUSH_RETRY_ATTEMPTS = 3
PUSH_RETRY_BASE_SECONDS = 1.0
PUSH_RETRY_MAX_SECONDS = 5.0

logger = structlog.get_logger(__name__)


class OutboxMixin(UserNotificationServiceBase):
    async def process_outbox(self, batch_size: int = 100) -> int:
        now = datetime.now(UTC)
        result = await self._db.execute(
            select(NotificationOutboxEvent)
            .where(NotificationOutboxEvent.status == "pending", NotificationOutboxEvent.available_at <= now)
            .order_by(NotificationOutboxEvent.created_at)
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )
        events = list(result.scalars().all())
        for event in events:
            event.status, event.attempts = "processing", event.attempts + 1
        await self._db.commit()
        completed = 0
        for event in events:
            try:
                await self._deliver_event(event)
                event.status, event.processed_at, event.last_error = "completed", datetime.now(UTC), None
                completed += 1
            except Exception as exc:  # retained for outbox retry diagnostics; no user data is logged
                event.status = "pending" if event.attempts < 5 else "failed"
                event.available_at = datetime.now(UTC) + timedelta(minutes=min(30, 2 ** event.attempts))
                event.last_error = type(exc).__name__
                logger.warning(
                    "notification_outbox_delivery_failed",
                    event_id=str(event.id),
                    event_type=event.event_type,
                    attempts=event.attempts,
                    error=type(exc).__name__,
                )
            await self._db.commit()
        return completed
    async def unreachable_recipients(self, tenant_id: UUID, limit: int = 100) -> list[UnreachableNotificationRecipient]:
        rows = await self._db.execute(
            select(UserNotification.recipient_user_id, User.display_name, func.count(UserNotification.id), func.max(UserNotification.created_at))
            .join(User, User.id == UserNotification.recipient_user_id)
            .where(UserNotification.tenant_id == tenant_id, UserNotification.read_at.is_(None))
            .group_by(UserNotification.recipient_user_id, User.display_name)
            .order_by(func.max(UserNotification.created_at).desc())
            .limit(limit)
        )
        outstanding = list(rows.all())
        if not outstanding:
            return []
        recipient_ids = [user_id for user_id, _, _, _ in outstanding]
        web_reachable = await self._web_reachable_user_ids(tenant_id, recipient_ids)
        firebase_reachable = await self._firebase_reachable_user_ids(tenant_id, recipient_ids)
        reachable = web_reachable | firebase_reachable
        return [
            UnreachableNotificationRecipient(
                user_id=user_id,
                display_name=display_name,
                pending_notifications=int(pending),
                last_notification_at=last_at,
            )
            for user_id, display_name, pending, last_at in outstanding
            if user_id not in reachable
        ]

    async def _web_reachable_user_ids(
        self, tenant_id: UUID, recipient_ids: list[UUID]
    ) -> set[UUID]:
        result = await self._db.execute(
            select(NotificationDeviceProfile.user_id)
            .select_from(WebPushSubscription)
            .join(
                NotificationDeviceProfile,
                NotificationDeviceProfile.device_id == WebPushSubscription.device_id,
            )
            .where(
                WebPushSubscription.tenant_id == tenant_id,
                WebPushSubscription.disabled_at.is_(None),
                NotificationDeviceProfile.user_id.in_(recipient_ids),
                NotificationDeviceProfile.push_enabled.is_(True),
                NotificationDeviceProfile.revoked_at.is_(None),
            )
            .distinct()
        )
        return set(result.scalars().all())

    async def _firebase_reachable_user_ids(
        self, tenant_id: UUID, recipient_ids: list[UUID]
    ) -> set[UUID]:
        result = await self._db.execute(
            select(NotificationDeviceProfile.user_id)
            .select_from(FirebasePushSubscription)
            .join(
                NotificationDeviceProfile,
                NotificationDeviceProfile.device_id == FirebasePushSubscription.device_id,
            )
            .where(
                FirebasePushSubscription.tenant_id == tenant_id,
                FirebasePushSubscription.disabled_at.is_(None),
                FirebasePushSubscription.recipient_user_id == NotificationDeviceProfile.user_id,
                NotificationDeviceProfile.user_id.in_(recipient_ids),
                NotificationDeviceProfile.push_enabled.is_(True),
                NotificationDeviceProfile.revoked_at.is_(None),
            )
            .distinct()
        )
        return set(result.scalars().all())
    async def _deliver_event(self, event: NotificationOutboxEvent) -> None:
        payload = json.loads(event.payload_json)
        recipients = [UUID(raw) for raw in payload.get("recipients", [])]
        event_id = payload.get("event_id")
        for recipient_id in recipients:
            notification = UserNotification(
                tenant_id=event.tenant_id,
                recipient_user_id=recipient_id,
                event_type=event.event_type,
                category=str(payload["category"]),
                priority=str(payload.get("priority", "normal")),
                target_path=str(payload["target_path"]),
                event_id=UUID(str(event_id)) if event_id else None,
                correlation_id=payload.get("correlation_id"),
                metadata_json=json.dumps(payload.get("metadata", {}), default=str),
                deduplication_key=f"{event.deduplication_key}:{recipient_id}",
            )
            self._db.add(notification)
        await self._db.flush()
        message = PushMessage(
            title=GENERIC_PUSH_TITLE,
            body=GENERIC_PUSH_BODY,
            target_path=str(payload["target_path"]),
        )
        await self._deliver_web_push(event.tenant_id, recipients, str(payload["category"]), message)
        await self._deliver_firebase_push(event.tenant_id, recipients, str(payload["category"]), message)
    def _web_push_active(self) -> bool:
        if self._web_push_provider is not None:
            return True
        return bool(
            settings.web_push_enabled
            and settings.web_push_vapid_private_key
            and settings.web_push_vapid_public_key
        )
    def _firebase_active(self) -> bool:
        if self._firebase_push_provider is not None:
            return True
        return bool(settings.firebase_messaging_enabled and settings.firebase_service_account_path)
    async def _send_with_retry(
        self,
        provider: WebPushProvider | FirebasePushProvider,
        target: WebPushTarget | FirebasePushTarget,
        message: PushMessage,
    ) -> PushOutcome:
        outcome = PushOutcome.TRANSIENT
        for attempt in range(PUSH_RETRY_ATTEMPTS):
            try:
                outcome = provider.send(target, message)
            except Exception:
                outcome = PushOutcome.TRANSIENT
            if outcome is not PushOutcome.TRANSIENT:
                return outcome
            if attempt < PUSH_RETRY_ATTEMPTS - 1:
                delay = min(PUSH_RETRY_BASE_SECONDS * (2**attempt), PUSH_RETRY_MAX_SECONDS)
                if delay > 0:
                    await asyncio.sleep(delay)
        return outcome
    async def _deliver_web_push(
        self,
        tenant_id: UUID,
        recipients: list[UUID],
        category: str,
        message: PushMessage,
    ) -> None:
        if not self._web_push_active():
            return
        rows = await self._db.execute(
            select(WebPushSubscription, NotificationDeviceProfile)
            .join(NotificationDeviceProfile, NotificationDeviceProfile.device_id == WebPushSubscription.device_id)
            .where(WebPushSubscription.tenant_id == tenant_id, WebPushSubscription.disabled_at.is_(None), NotificationDeviceProfile.user_id.in_(recipients), NotificationDeviceProfile.push_enabled.is_(True), NotificationDeviceProfile.revoked_at.is_(None))
        )
        delivered: set[UUID] = set()
        for subscription, profile in rows.all():
            if subscription.id in delivered:
                continue
            if not self._preferences_from_profile(profile).get(f"{category}_enabled", True):
                continue
            delivered.add(subscription.id)
            outcome = await self._send_with_retry(
                self.web_push_provider,
                WebPushTarget(
                    endpoint=subscription.endpoint,
                    p256dh=subscription.p256dh,
                    auth=subscription.auth,
                ),
                message,
            )
            metrics.record_push_delivery("web_push", outcome.value)
            if outcome is PushOutcome.DELIVERED:
                continue
            if outcome is PushOutcome.INVALID_TARGET:
                subscription.disabled_at = datetime.now(UTC)
            else:
                subscription.failure_count += 1
    async def _deliver_firebase_push(
        self,
        tenant_id: UUID,
        recipients: list[UUID],
        category: str,
        message: PushMessage,
    ) -> None:
        if not self._firebase_active():
            return
        rows = await self._db.execute(
            select(FirebasePushSubscription, NotificationDeviceProfile)
            .join(NotificationDeviceProfile, NotificationDeviceProfile.device_id == FirebasePushSubscription.device_id)
            .where(
                FirebasePushSubscription.tenant_id == tenant_id,
                FirebasePushSubscription.disabled_at.is_(None),
                FirebasePushSubscription.recipient_user_id.in_(recipients),
                NotificationDeviceProfile.user_id.in_(recipients),
                FirebasePushSubscription.recipient_user_id == NotificationDeviceProfile.user_id,
                NotificationDeviceProfile.push_enabled.is_(True),
                NotificationDeviceProfile.revoked_at.is_(None),
            )
        )
        for subscription, profile in rows.all():
            if not self._preferences_from_profile(profile).get(f"{category}_enabled", True):
                continue
            outcome = await self._send_with_retry(
                self.firebase_push_provider,
                FirebasePushTarget(token=subscription.fcm_token),
                message,
            )
            metrics.record_push_delivery("firebase", outcome.value)
            if outcome is PushOutcome.DELIVERED:
                continue
            if outcome is PushOutcome.INVALID_TARGET:
                subscription.disabled_at = datetime.now(UTC)
            else:
                subscription.failure_count += 1
        await self._db.commit()
