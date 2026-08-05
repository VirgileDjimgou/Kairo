from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class InboxNotificationResponse(BaseModel):
    id: UUID
    event_type: str
    category: str
    priority: str
    target_path: str
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


class PushSubscriptionRequest(DeviceRegistrationRequest):
    endpoint: str = Field(min_length=12, max_length=4096)
    p256dh: str = Field(min_length=8, max_length=2048)
    auth: str = Field(min_length=8, max_length=2048)


class PushConfigurationResponse(BaseModel):
    enabled: bool
    public_key: str | None = None
    reason: str | None = None


class UnreachableNotificationRecipient(BaseModel):
    user_id: UUID
    display_name: str
    pending_notifications: int
    last_notification_at: datetime
