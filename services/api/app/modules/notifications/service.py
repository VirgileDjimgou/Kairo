from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.notifications.schemas import (
    NotificationChannelResponse,
    NotificationDispatchResponse,
    NotificationTestRequest,
    NotificationTestResponse,
)
from app.providers.notifications.base import NotificationProvider


class NotificationService:
    def __init__(self, providers: list[NotificationProvider]) -> None:
        self._providers = providers
        self._provider_map = {provider.channel: provider for provider in providers}

    def list_channels(self) -> list[NotificationChannelResponse]:
        return [
            NotificationChannelResponse(
                channel=descriptor.channel,
                display_name=descriptor.display_name,
                description=descriptor.description,
                configured=descriptor.configured,
                simulation_only=descriptor.simulation_only,
                target_hint=descriptor.target_hint,
            )
            for descriptor in (provider.describe() for provider in self._providers)
        ]

    async def send_test(
        self,
        *,
        tenant_id,
        actor_user_id,
        payload: NotificationTestRequest,
    ) -> NotificationTestResponse:
        unique_channels: list[str] = []
        for channel in payload.channels:
            if channel not in unique_channels:
                unique_channels.append(channel)

        unknown = [channel for channel in unique_channels if channel not in self._provider_map]
        if unknown:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown notification channel(s): {', '.join(sorted(unknown))}",
            )

        results: list[NotificationDispatchResponse] = []
        for channel in unique_channels:
            provider = self._provider_map[channel]
            dispatched = await provider.send_test_message(
                tenant_id=tenant_id,
                actor_user_id=actor_user_id,
                recipient=payload.recipient,
                subject=payload.subject,
                body=payload.body,
            )
            results.append(
                NotificationDispatchResponse(
                    channel=dispatched.channel,
                    status=dispatched.status,
                    message=dispatched.message,
                    delivered=dispatched.delivered,
                    simulation_only=dispatched.simulation_only,
                )
            )

        return NotificationTestResponse(results=results)
