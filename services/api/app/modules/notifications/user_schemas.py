from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class InboxNotificationResponse(BaseModel):
    id: UUID
    event_type: str
    category: str
    priority: str
    target_path: str
    event_id: UUID | None = None
    correlation_id: str | None = None
    metadata: dict[str, object]
    read_at: datetime | None
    created_at: datetime


class InboxResponse(BaseModel):
    items: list[InboxNotificationResponse]
    unread_count: int


class NotificationPreferencesResponse(BaseModel):
    push_enabled: bool = True
    finance_enabled: bool = True
    discipline_enabled: bool = True
    announcements_enabled: bool = True
    events_enabled: bool = True


class NotificationPreferencesUpdate(BaseModel):
    push_enabled: bool = True
    finance_enabled: bool = True
    discipline_enabled: bool = True
    announcements_enabled: bool = True
    events_enabled: bool = True


class DeviceRegistrationRequest(BaseModel):
    installation_id: str = Field(min_length=16, max_length=128)
    platform: str | None = Field(default=None, max_length=80)
    browser: str | None = Field(default=None, max_length=80)
    device_metadata: dict[str, str | int | bool | None] = Field(default_factory=dict)

    @field_validator("device_metadata")
    @classmethod
    def validate_device_metadata(
        cls, value: dict[str, str | int | bool | None]
    ) -> dict[str, str | int | bool | None]:
        if len(value) > 12:
            raise ValueError("device_metadata accepts at most 12 entries")
        for key, item in value.items():
            if not key or len(key) > 40:
                raise ValueError("device_metadata keys must be between 1 and 40 characters")
            if isinstance(item, str) and len(item) > 200:
                raise ValueError("device_metadata string values must be at most 200 characters")
        return value


class PushSubscriptionRequest(DeviceRegistrationRequest):
    endpoint: str = Field(min_length=12, max_length=4096)
    p256dh: str = Field(min_length=8, max_length=2048)
    auth: str = Field(min_length=8, max_length=2048)


class MobilePushTokenRequest(DeviceRegistrationRequest):
    fcm_token: str = Field(min_length=32, max_length=4096)


class PushConfigurationResponse(BaseModel):
    enabled: bool
    public_key: str | None = None
    reason: str | None = None


class UnreachableNotificationRecipient(BaseModel):
    user_id: UUID
    display_name: str
    pending_notifications: int
    last_notification_at: datetime


class NotificationHealthResponse(BaseModel):
    web_push_configured: bool
    firebase_configured: bool
    worker_running: bool
    pending_outbox: int
    failed_outbox: int
    oldest_pending_seconds: int | None = None
    disabled_web_subscriptions: int
    disabled_fcm_tokens: int
    retrying_web_subscriptions: int = 0
    retrying_fcm_tokens: int = 0
    last_successful_dispatch_at: datetime | None = None


class NotificationDeviceRevocationResponse(BaseModel):
    revoked_profiles: int
    disabled_web_subscriptions: int
    disabled_fcm_tokens: int
