from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Iterable
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.identity.models import User
from app.modules.notifications.user_models import (
    NotificationDevice,
    NotificationDeviceProfile,
    NotificationOutboxEvent,
    UserNotification,
    WebPushSubscription,
)
from app.modules.notifications.user_schemas import (
    InboxNotificationResponse,
    InboxResponse,
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate,
    UnreachableNotificationRecipient,
)
from app.modules.tenancy.models import Role, TenantUser, UserRole


class UserNotificationService:
    """Inbox, device binding and asynchronous Web Push dispatch.

    Browser push payloads are deliberately generic: the user must authenticate
    before seeing any financial or disciplinary detail in the inbox.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def enqueue(
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
    ) -> None:
        recipient_ids = sorted({str(user_id) for user_id in recipients})
        if not recipient_ids:
            return
        event = NotificationOutboxEvent(
            tenant_id=tenant_id,
            event_type=event_type,
            deduplication_key=deduplication_key,
            payload_json=json.dumps({
                "recipients": recipient_ids,
                "category": category,
                "target_path": target_path,
                "metadata": metadata or {},
                "priority": priority,
            }, default=str),
        )
        self._db.add(event)

    async def users_with_roles(self, tenant_id: UUID, role_codes: Iterable[str]) -> list[UUID]:
        codes = list(set(role_codes))
        if not codes:
            return []
        result = await self._db.execute(
            select(TenantUser.user_id)
            .select_from(TenantUser)
            .join(UserRole, UserRole.c.tenant_user_id == TenantUser.id)
            .join(Role, Role.id == UserRole.c.role_id)
            .where(TenantUser.tenant_id == tenant_id, TenantUser.membership_status == "active", Role.code.in_(codes))
        )
        return list(set(result.scalars().all()))

    async def active_tenant_users(self, tenant_id: UUID) -> list[UUID]:
        result = await self._db.execute(
            select(TenantUser.user_id).where(
                TenantUser.tenant_id == tenant_id,
                TenantUser.membership_status == "active",
            )
        )
        return list(set(result.scalars().all()))

    async def inbox(self, tenant_id: UUID, user_id: UUID, limit: int = 50) -> InboxResponse:
        result = await self._db.execute(
            select(UserNotification)
            .where(UserNotification.tenant_id == tenant_id, UserNotification.recipient_user_id == user_id)
            .order_by(UserNotification.created_at.desc())
            .limit(limit)
        )
        items = list(result.scalars().all())
        unread = await self._db.scalar(
            select(func.count(UserNotification.id)).where(
                UserNotification.tenant_id == tenant_id,
                UserNotification.recipient_user_id == user_id,
                UserNotification.read_at.is_(None),
            )
        )
        return InboxResponse(
            unread_count=int(unread or 0),
            items=[self._to_response(item) for item in items],
        )

    async def mark_read(self, tenant_id: UUID, user_id: UUID, notification_id: UUID) -> bool:
        result = await self._db.execute(
            update(UserNotification)
            .where(UserNotification.id == notification_id, UserNotification.tenant_id == tenant_id, UserNotification.recipient_user_id == user_id)
            .values(read_at=datetime.now(UTC))
        )
        await self._db.commit()
        return bool(result.rowcount)

    async def mark_all_read(self, tenant_id: UUID, user_id: UUID) -> None:
        await self._db.execute(
            update(UserNotification)
            .where(UserNotification.tenant_id == tenant_id, UserNotification.recipient_user_id == user_id, UserNotification.read_at.is_(None))
            .values(read_at=datetime.now(UTC))
        )
        await self._db.commit()

    async def preferences(self, tenant_id: UUID, user_id: UUID) -> NotificationPreferencesResponse:
        profile = await self._profile(tenant_id, user_id)
        values = self._preferences_from_profile(profile)
        return NotificationPreferencesResponse(**values)

    async def update_preferences(self, tenant_id: UUID, user_id: UUID, values: NotificationPreferencesUpdate) -> NotificationPreferencesResponse:
        profile = await self._profile(tenant_id, user_id)
        profile.push_enabled = values.push_enabled
        profile.preferences_json = json.dumps(values.model_dump())
        await self._db.commit()
        return NotificationPreferencesResponse(**values.model_dump())

    async def register_device(self, tenant_id: UUID, user_id: UUID, installation_id: str, platform: str | None, user_agent: str | None) -> NotificationDevice:
        result = await self._db.execute(select(NotificationDevice).where(NotificationDevice.tenant_id == tenant_id, NotificationDevice.installation_id == installation_id))
        device = result.scalar_one_or_none()
        if device is None:
            device = NotificationDevice(tenant_id=tenant_id, installation_id=installation_id, platform=platform, user_agent=user_agent)
            self._db.add(device)
            await self._db.flush()
        else:
            device.platform = platform or device.platform
            device.user_agent = user_agent or device.user_agent
            device.last_seen_at = datetime.now(UTC)
        await self._ensure_profile(tenant_id, device.id, user_id)
        await self._db.commit()
        return device

    async def save_subscription(self, tenant_id: UUID, user_id: UUID, installation_id: str, platform: str | None, user_agent: str | None, endpoint: str, p256dh: str, auth: str) -> None:
        device = await self.register_device(tenant_id, user_id, installation_id, platform, user_agent)
        result = await self._db.execute(select(WebPushSubscription).where(WebPushSubscription.device_id == device.id, WebPushSubscription.endpoint == endpoint))
        subscription = result.scalar_one_or_none()
        if subscription is None:
            self._db.add(WebPushSubscription(tenant_id=tenant_id, device_id=device.id, endpoint=endpoint, p256dh=p256dh, auth=auth))
        else:
            subscription.p256dh, subscription.auth = p256dh, auth
            subscription.disabled_at, subscription.failure_count, subscription.updated_at = None, 0, datetime.now(UTC)
        profile = await self._profile(tenant_id, user_id, device.id)
        profile.push_enabled, profile.opted_in_at, profile.revoked_at = True, datetime.now(UTC), None
        await self._db.commit()

    async def push_configuration(self) -> dict[str, object]:
        if not settings.web_push_enabled:
            return {"enabled": False, "reason": "disabled"}
        if not settings.web_push_vapid_public_key or not settings.web_push_vapid_private_key:
            return {"enabled": False, "reason": "not_configured"}
        return {"enabled": True, "public_key": settings.web_push_vapid_public_key}

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
        result: list[UnreachableNotificationRecipient] = []
        for user_id, display_name, pending, last_at in rows.all():
            reachable = await self._db.scalar(
                select(func.count(WebPushSubscription.id))
                .select_from(WebPushSubscription)
                .join(NotificationDeviceProfile, NotificationDeviceProfile.device_id == WebPushSubscription.device_id)
                .where(WebPushSubscription.tenant_id == tenant_id, WebPushSubscription.disabled_at.is_(None), NotificationDeviceProfile.user_id == user_id, NotificationDeviceProfile.push_enabled.is_(True), NotificationDeviceProfile.revoked_at.is_(None))
            )
            if not reachable:
                result.append(UnreachableNotificationRecipient(user_id=user_id, display_name=display_name, pending_notifications=int(pending), last_notification_at=last_at))
        return result

    async def _deliver_event(self, event: NotificationOutboxEvent) -> None:
        payload = json.loads(event.payload_json)
        recipients = [UUID(raw) for raw in payload.get("recipients", [])]
        for recipient_id in recipients:
            notification = UserNotification(
                tenant_id=event.tenant_id,
                recipient_user_id=recipient_id,
                event_type=event.event_type,
                category=str(payload["category"]),
                priority=str(payload.get("priority", "normal")),
                target_path=str(payload["target_path"]),
                metadata_json=json.dumps(payload.get("metadata", {}), default=str),
                deduplication_key=f"{event.deduplication_key}:{recipient_id}",
            )
            self._db.add(notification)
        await self._db.flush()
        await self._send_generic_push(
            event.tenant_id,
            recipients,
            str(payload["category"]),
            str(payload["target_path"]),
        )

    async def _send_generic_push(
        self,
        tenant_id: UUID,
        recipients: list[UUID],
        category: str,
        target_path: str,
    ) -> None:
        if not settings.web_push_enabled or not settings.web_push_vapid_private_key or not settings.web_push_vapid_public_key:
            return
        try:
            from pywebpush import WebPushException, webpush
        except ImportError:
            return
        rows = await self._db.execute(
            select(WebPushSubscription, NotificationDeviceProfile)
            .join(NotificationDeviceProfile, NotificationDeviceProfile.device_id == WebPushSubscription.device_id)
            .where(WebPushSubscription.tenant_id == tenant_id, WebPushSubscription.disabled_at.is_(None), NotificationDeviceProfile.user_id.in_(recipients), NotificationDeviceProfile.push_enabled.is_(True), NotificationDeviceProfile.revoked_at.is_(None))
        )
        for subscription, profile in rows.all():
            if not self._preferences_from_profile(profile).get(f"{category}_enabled", True):
                continue
            try:
                webpush(subscription_info={"endpoint": subscription.endpoint, "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth}}, data=json.dumps({"title": "Kairo", "body": "Une nouvelle notification est disponible.", "url": target_path}), vapid_private_key=settings.web_push_vapid_private_key.replace(r"\n", "\n"), vapid_claims={"sub": settings.web_push_vapid_subject})
            except WebPushException as exc:
                subscription.failure_count += 1
                if getattr(exc, "response", None) is not None and exc.response.status_code in {404, 410}:
                    subscription.disabled_at = datetime.now(UTC)
            except Exception:
                # Push is a delivery hint only. A transient vendor/network error
                # must not block the authenticated inbox or outbox completion.
                subscription.failure_count += 1

    async def _ensure_profile(self, tenant_id: UUID, device_id: UUID, user_id: UUID) -> NotificationDeviceProfile:
        result = await self._db.execute(select(NotificationDeviceProfile).where(NotificationDeviceProfile.device_id == device_id, NotificationDeviceProfile.user_id == user_id))
        profile = result.scalar_one_or_none()
        if profile is None:
            profile = NotificationDeviceProfile(tenant_id=tenant_id, device_id=device_id, user_id=user_id)
            self._db.add(profile)
            await self._db.flush()
        return profile

    async def _profile(self, tenant_id: UUID, user_id: UUID, device_id: UUID | None = None) -> NotificationDeviceProfile:
        statement = select(NotificationDeviceProfile).where(NotificationDeviceProfile.tenant_id == tenant_id, NotificationDeviceProfile.user_id == user_id)
        if device_id is not None:
            statement = statement.where(NotificationDeviceProfile.device_id == device_id)
        profile = (await self._db.execute(statement)).scalar_one_or_none()
        if profile is None:
            raise RuntimeError("Notification device profile has not been registered")
        return profile

    def _preferences_from_profile(self, profile: NotificationDeviceProfile) -> dict[str, bool]:
        defaults = {"push_enabled": profile.push_enabled, "finance_enabled": True, "discipline_enabled": True, "announcements_enabled": True, "events_enabled": True}
        try:
            stored = json.loads(profile.preferences_json)
        except json.JSONDecodeError:
            stored = {}
        if isinstance(stored, dict):
            for key in defaults:
                if key in stored:
                    defaults[key] = bool(stored[key])
        defaults["push_enabled"] = profile.push_enabled
        return defaults

    def _to_response(self, item: UserNotification) -> InboxNotificationResponse:
        try:
            metadata = json.loads(item.metadata_json)
        except json.JSONDecodeError:
            metadata = {}
        return InboxNotificationResponse(id=item.id, event_type=item.event_type, category=item.category, priority=item.priority, target_path=item.target_path, metadata=metadata if isinstance(metadata, dict) else {}, read_at=item.read_at, created_at=item.created_at)
