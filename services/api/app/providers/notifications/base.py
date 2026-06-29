from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class NotificationChannelDescriptor:
    channel: str
    display_name: str
    description: str
    configured: bool
    simulation_only: bool
    target_hint: str


@dataclass(frozen=True)
class NotificationDispatchResult:
    channel: str
    status: str
    message: str
    delivered: bool
    simulation_only: bool


class NotificationProvider(Protocol):
    channel: str

    def describe(self) -> NotificationChannelDescriptor: ...

    async def send_message(
        self,
        *,
        tenant_id: UUID,
        actor_user_id: UUID | None,
        recipient: str,
        subject: str | None,
        body: str,
    ) -> NotificationDispatchResult: ...

    async def send_test_message(
        self,
        *,
        tenant_id: UUID,
        actor_user_id: UUID,
        recipient: str,
        subject: str | None,
        body: str,
    ) -> NotificationDispatchResult: ...
