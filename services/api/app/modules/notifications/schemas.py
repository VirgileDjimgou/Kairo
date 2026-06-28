from __future__ import annotations

from pydantic import BaseModel, Field


class NotificationChannelResponse(BaseModel):
    channel: str
    display_name: str
    description: str
    configured: bool
    simulation_only: bool
    target_hint: str


class NotificationTestRequest(BaseModel):
    channels: list[str] = Field(min_length=1)
    recipient: str = Field(min_length=1, max_length=255)
    subject: str | None = Field(default=None, max_length=255)
    body: str = Field(min_length=1, max_length=4000)


class NotificationDispatchResponse(BaseModel):
    channel: str
    status: str
    message: str
    delivered: bool
    simulation_only: bool


class NotificationTestResponse(BaseModel):
    results: list[NotificationDispatchResponse]
