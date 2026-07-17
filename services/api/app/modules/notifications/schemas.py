from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationChannelResponse(BaseModel):
    channel: str
    display_name: str
    description: str
    configured: bool
    simulation_only: bool
    target_hint: str
    polling_supported: bool = False


class NotificationTestRequest(BaseModel):
    channels: list[str] = Field(min_length=1)
    recipient: str = Field(min_length=1, max_length=255)
    subject: str | None = Field(default=None, max_length=255)
    body: str = Field(min_length=1, max_length=4000)


class NotificationDispatchRequest(BaseModel):
    channel: str = Field(min_length=1, max_length=50)
    recipient: str = Field(min_length=1, max_length=255)
    subject: str | None = Field(default=None, max_length=255)
    body: str = Field(min_length=1, max_length=4000)


class NotificationDispatchResponse(BaseModel):
    channel: str
    status: str
    message: str
    delivered: bool
    simulation_only: bool
    delivery_stage: str
    reconciliation_status: str
    reconciliation_supported: bool
    provider_reference: str | None = None
    polling_supported: bool = False


class NotificationHistoryEntry(BaseModel):
    id: UUID
    action: str
    channel: str
    recipient: str
    status: str
    message: str
    delivered: bool
    simulation_only: bool
    delivery_stage: str
    reconciliation_status: str
    reconciliation_supported: bool
    provider_reference: str | None = None
    polling_supported: bool = False
    created_at: datetime


class NotificationReconciliationCallbackRequest(BaseModel):
    tenant_id: UUID
    channel: str = Field(min_length=1, max_length=50)
    provider_reference: str = Field(min_length=1, max_length=255)
    delivery_stage: Literal["delivered", "failed"]
    provider_message: str | None = Field(default=None, max_length=4000)
    external_status: str | None = Field(default=None, max_length=100)


class NotificationReconciliationCallbackResponse(BaseModel):
    channel: str
    provider_reference: str
    delivery_stage: str
    reconciliation_status: str
    updated: bool


class NotificationReconciliationPollRequest(BaseModel):
    channel: str = Field(min_length=1, max_length=50)
    provider_reference: str = Field(min_length=1, max_length=255)


class NotificationReconciliationPollResponse(BaseModel):
    channel: str
    provider_reference: str
    delivery_stage: str
    reconciliation_status: str
    updated: bool
    provider_message: str
    external_status: str | None = None


class NotificationTestResponse(BaseModel):
    results: list[NotificationDispatchResponse]
