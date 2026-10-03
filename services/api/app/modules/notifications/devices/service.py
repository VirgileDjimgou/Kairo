from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select

from app.core.config import settings
from app.modules.notifications.user_base import UserNotificationServiceBase
from app.modules.notifications.user_models import (
    FirebasePushSubscription,
    NotificationDevice,
    NotificationDeviceProfile,
    WebPushSubscription,
)


class DevicesMixin(UserNotificationServiceBase):
    async def register_device(
        self,
        tenant_id: UUID,
        user_id: UUID,
        installation_id: str,
        platform: str | None,
        user_agent: str | None,
        browser: str | None = None,
        device_metadata: dict[str, object] | None = None,
    ) -> NotificationDevice:
        result = await self._db.execute(select(NotificationDevice).where(NotificationDevice.tenant_id == tenant_id, NotificationDevice.installation_id == installation_id))
        device = result.scalar_one_or_none()
        now = datetime.now(UTC)
        metadata_json = json.dumps(device_metadata or {}, default=str)
        if device is None:
            device = NotificationDevice(
                tenant_id=tenant_id,
                installation_id=installation_id,
                platform=platform,
                browser=browser,
                user_agent=user_agent,
                device_metadata_json=metadata_json,
                status="active",
            )
            self._db.add(device)
            await self._db.flush()
        else:
            device.platform = platform or device.platform
            device.browser = browser or device.browser
            device.user_agent = user_agent or device.user_agent
            if device_metadata:
                device.device_metadata_json = metadata_json
            device.status = "active"
            device.revoked_at = None
            device.last_seen_at = now
            device.updated_at = now
        await self._ensure_profile(tenant_id, device.id, user_id)
        await self._db.commit()
        return device

    async def save_subscription(
        self,
        tenant_id: UUID,
        user_id: UUID,
        installation_id: str,
        platform: str | None,
        user_agent: str | None,
        endpoint: str,
        p256dh: str,
        auth: str,
        browser: str | None = None,
        device_metadata: dict[str, object] | None = None,
    ) -> None:
        device = await self.register_device(
            tenant_id, user_id, installation_id, platform, user_agent, browser, device_metadata
        )
        result = await self._db.execute(select(WebPushSubscription).where(WebPushSubscription.device_id == device.id, WebPushSubscription.endpoint == endpoint))
        subscription = result.scalar_one_or_none()
        if subscription is None:
            self._db.add(WebPushSubscription(tenant_id=tenant_id, device_id=device.id, provider="web_push", endpoint=endpoint, p256dh=p256dh, auth=auth))
        else:
            subscription.p256dh, subscription.auth = p256dh, auth
            subscription.disabled_at, subscription.failure_count, subscription.updated_at = None, 0, datetime.now(UTC)
        profile = await self._profile(tenant_id, user_id, device.id)
        profile.push_enabled, profile.opted_in_at, profile.revoked_at = True, datetime.now(UTC), None
        await self._db.commit()

    async def save_firebase_subscription(
        self,
        tenant_id: UUID,
        user_id: UUID,
        installation_id: str,
        user_agent: str | None,
        fcm_token: str,
        platform: str | None = None,
        browser: str | None = None,
        device_metadata: dict[str, object] | None = None,
    ) -> None:
        device = await self.register_device(
            tenant_id, user_id, installation_id, platform or "android", user_agent, browser, device_metadata
        )
        now = datetime.now(UTC)
        # Token rotation: a refreshed FCM token replaces obsolete active tokens
        # for this installation/profile so a device is never delivered twice.
        rotated = list(
            (
                await self._db.execute(
                    select(FirebasePushSubscription).where(
                        FirebasePushSubscription.device_id == device.id,
                        FirebasePushSubscription.recipient_user_id == user_id,
                        FirebasePushSubscription.fcm_token != fcm_token,
                        FirebasePushSubscription.disabled_at.is_(None),
                    )
                )
            ).scalars()
        )
        for obsolete in rotated:
            obsolete.disabled_at = now
        result = await self._db.execute(
            select(FirebasePushSubscription).where(
                FirebasePushSubscription.device_id == device.id,
                FirebasePushSubscription.fcm_token == fcm_token,
            )
        )
        subscription = result.scalar_one_or_none()
        if subscription is None:
            self._db.add(FirebasePushSubscription(
                tenant_id=tenant_id,
                device_id=device.id,
                recipient_user_id=user_id,
                provider="firebase",
                platform=device.platform,
                fcm_token=fcm_token,
            ))
        else:
            subscription.recipient_user_id = user_id
            subscription.provider = "firebase"
            subscription.platform = device.platform
            subscription.disabled_at = None
            subscription.failure_count = 0
            subscription.updated_at = now
        profile = await self._profile(tenant_id, user_id, device.id)
        profile.push_enabled, profile.opted_in_at, profile.revoked_at = True, now, None
        await self._db.commit()

    async def _refresh_device_status(self, tenant_id: UUID, device: NotificationDevice) -> None:
        """Mark an installation revoked only when no profile or provider remains."""
        active_profiles = int(
            await self._db.scalar(
                select(func.count(NotificationDeviceProfile.id)).where(
                    NotificationDeviceProfile.tenant_id == tenant_id,
                    NotificationDeviceProfile.device_id == device.id,
                    NotificationDeviceProfile.revoked_at.is_(None),
                )
            )
            or 0
        )
        active_web = int(
            await self._db.scalar(
                select(func.count(WebPushSubscription.id)).where(
                    WebPushSubscription.tenant_id == tenant_id,
                    WebPushSubscription.device_id == device.id,
                    WebPushSubscription.disabled_at.is_(None),
                )
            )
            or 0
        )
        active_firebase = int(
            await self._db.scalar(
                select(func.count(FirebasePushSubscription.id)).where(
                    FirebasePushSubscription.tenant_id == tenant_id,
                    FirebasePushSubscription.device_id == device.id,
                    FirebasePushSubscription.disabled_at.is_(None),
                )
            )
            or 0
        )
        now = datetime.now(UTC)
        if active_profiles == 0 and active_web == 0 and active_firebase == 0:
            device.status = "revoked"
            device.revoked_at = now
        else:
            device.status = "active"
            device.revoked_at = None
        device.updated_at = now

    async def push_configuration(self) -> dict[str, object]:
        if not settings.web_push_enabled:
            return {"enabled": False, "reason": "disabled"}
        if not settings.web_push_vapid_public_key or not settings.web_push_vapid_private_key:
            return {"enabled": False, "reason": "not_configured"}
        return {"enabled": True, "public_key": settings.web_push_vapid_public_key}

    async def revoke_device(
        self, tenant_id: UUID, user_id: UUID, installation_id: str
    ) -> tuple[int, int, int]:
        """Revoke this user's profile binding on one installation.

        The installation identity row is preserved so a later sign-in re-registers
        and re-enables delivery without leaking the previous account's push.
        """
        device = (
            await self._db.execute(
                select(NotificationDevice).where(
                    NotificationDevice.tenant_id == tenant_id,
                    NotificationDevice.installation_id == installation_id,
                )
            )
        ).scalar_one_or_none()
        if device is None:
            return (0, 0, 0)
        now = datetime.now(UTC)
        profiles = list(
            (
                await self._db.execute(
                    select(NotificationDeviceProfile).where(
                        NotificationDeviceProfile.tenant_id == tenant_id,
                        NotificationDeviceProfile.device_id == device.id,
                        NotificationDeviceProfile.user_id == user_id,
                    )
                )
            ).scalars()
        )
        for profile in profiles:
            profile.revoked_at = now
            profile.push_enabled = False
        await self._db.flush()
        remaining_profiles = int(
            await self._db.scalar(
                select(func.count(NotificationDeviceProfile.id)).where(
                    NotificationDeviceProfile.tenant_id == tenant_id,
                    NotificationDeviceProfile.device_id == device.id,
                    NotificationDeviceProfile.revoked_at.is_(None),
                )
            )
            or 0
        )
        web_subscriptions: list[WebPushSubscription] = []
        if remaining_profiles == 0:
            web_subscriptions = list(
                (
                    await self._db.execute(
                        select(WebPushSubscription).where(
                            WebPushSubscription.tenant_id == tenant_id,
                            WebPushSubscription.device_id == device.id,
                            WebPushSubscription.disabled_at.is_(None),
                        )
                    )
                ).scalars()
            )
            for subscription in web_subscriptions:
                subscription.disabled_at = now
        firebase_subscriptions = list(
            (
                await self._db.execute(
                    select(FirebasePushSubscription).where(
                        FirebasePushSubscription.tenant_id == tenant_id,
                        FirebasePushSubscription.device_id == device.id,
                        FirebasePushSubscription.recipient_user_id == user_id,
                        FirebasePushSubscription.disabled_at.is_(None),
                    )
                )
            ).scalars()
        )
        for subscription in firebase_subscriptions:
            subscription.disabled_at = now
        await self._db.flush()
        await self._refresh_device_status(tenant_id, device)
        await self._db.commit()
        return (len(profiles), len(web_subscriptions), len(firebase_subscriptions))

    async def revoke_all_devices(self, tenant_id: UUID, user_id: UUID) -> tuple[int, int, int]:
        """Revoke every push binding of a user in a tenant (session termination)."""
        now = datetime.now(UTC)
        profiles = list(
            (
                await self._db.execute(
                    select(NotificationDeviceProfile).where(
                        NotificationDeviceProfile.tenant_id == tenant_id,
                        NotificationDeviceProfile.user_id == user_id,
                    )
                )
            ).scalars()
        )
        device_ids = [profile.device_id for profile in profiles]
        for profile in profiles:
            profile.revoked_at = now
            profile.push_enabled = False
        await self._db.flush()
        web_subscriptions: list[WebPushSubscription] = []
        if device_ids:
            shared_device_ids = set(
                (
                    await self._db.execute(
                        select(NotificationDeviceProfile.device_id).where(
                            NotificationDeviceProfile.tenant_id == tenant_id,
                            NotificationDeviceProfile.device_id.in_(device_ids),
                            NotificationDeviceProfile.revoked_at.is_(None),
                        )
                    )
                )
                .scalars()
                .all()
            )
            revocable_device_ids = [
                device_id for device_id in device_ids if device_id not in shared_device_ids
            ]
            if revocable_device_ids:
                web_subscriptions = list(
                    (
                        await self._db.execute(
                            select(WebPushSubscription).where(
                                WebPushSubscription.tenant_id == tenant_id,
                                WebPushSubscription.device_id.in_(revocable_device_ids),
                                WebPushSubscription.disabled_at.is_(None),
                            )
                        )
                    ).scalars()
                )
                for subscription in web_subscriptions:
                    subscription.disabled_at = now
        firebase_subscriptions = list(
            (
                await self._db.execute(
                    select(FirebasePushSubscription).where(
                        FirebasePushSubscription.tenant_id == tenant_id,
                        FirebasePushSubscription.recipient_user_id == user_id,
                        FirebasePushSubscription.disabled_at.is_(None),
                    )
                )
            ).scalars()
        )
        for subscription in firebase_subscriptions:
            subscription.disabled_at = now
        await self._db.flush()
        if device_ids:
            devices = list(
                (
                    await self._db.execute(
                        select(NotificationDevice).where(
                            NotificationDevice.tenant_id == tenant_id,
                            NotificationDevice.id.in_(device_ids),
                        )
                    )
                ).scalars()
            )
            for device in devices:
                await self._refresh_device_status(tenant_id, device)
        await self._db.commit()
        return (len(profiles), len(web_subscriptions), len(firebase_subscriptions))
