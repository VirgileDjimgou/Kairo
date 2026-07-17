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
    polling_supported: bool = False


@dataclass(frozen=True)
class NotificationDispatchResult:
    channel: str
    status: str
    message: str
    delivered: bool
    simulation_only: bool
    delivery_stage: str = "simulated"
    reconciliation_status: str = "not_applicable"
    reconciliation_supported: bool = False
    provider_reference: str | None = None
    polling_supported: bool = False


@dataclass(frozen=True)
class NotificationDeliveryStatusResult:
    delivery_stage: str
    reconciliation_status: str
    delivered: bool
    provider_message: str
    external_status: str | None = None
    terminal: bool = False


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

    async def fetch_delivery_status(
        self,
        *,
        tenant_id: UUID,
        actor_user_id: UUID | None,
        recipient: str,
        provider_reference: str,
    ) -> NotificationDeliveryStatusResult | None: ...
