from __future__ import annotations

import json
from uuid import UUID

from sqlalchemy import select

from app.modules.notifications.user_base import UserNotificationServiceBase
from app.modules.notifications.user_models import (
    NotificationDeviceProfile,
)
from app.modules.notifications.user_schemas import (
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate,
)


class PreferencesMixin(UserNotificationServiceBase):
    async def preferences(self, tenant_id: UUID, user_id: UUID) -> NotificationPreferencesResponse:
        profile = await self._profile(tenant_id, user_id)
        values = self._preferences_from_profile(profile)
        return NotificationPreferencesResponse(**values)
    async def update_preferences(self, tenant_id: UUID, user_id: UUID, values: NotificationPreferencesUpdate) -> NotificationPreferencesResponse:
        profiles = await self._profiles(tenant_id, user_id)
        if not profiles:
            raise RuntimeError("Notification device profile has not been registered")
        serialized = json.dumps(values.model_dump())
        for profile in profiles:
            profile.push_enabled = values.push_enabled
            profile.preferences_json = serialized
        await self._db.commit()
        return NotificationPreferencesResponse(**values.model_dump())
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
        else:
            # Preferences are account-level in the current API contract. A user
            # can legitimately bind several browsers or Android installations,
            # so reading them must never assume there is only one device row.
            statement = statement.order_by(
                NotificationDeviceProfile.opted_in_at.desc().nullslast(),
                NotificationDeviceProfile.id,
            ).limit(1)
        profile = (await self._db.execute(statement)).scalar_one_or_none()
        if profile is None:
            raise RuntimeError("Notification device profile has not been registered")
        return profile
    async def _profiles(self, tenant_id: UUID, user_id: UUID) -> list[NotificationDeviceProfile]:
        result = await self._db.execute(
            select(NotificationDeviceProfile).where(
                NotificationDeviceProfile.tenant_id == tenant_id,
                NotificationDeviceProfile.user_id == user_id,
            )
        )
        return list(result.scalars().all())
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
