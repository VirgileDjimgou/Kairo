from __future__ import annotations

import json

from fastapi import HTTPException, status

from app.modules.notifications.schemas import (
    NotificationChannelResponse,
    NotificationDispatchRequest,
    NotificationDispatchResponse,
    NotificationTestRequest,
    NotificationTestResponse,
)
from app.modules.notifications.service_base import (
    NotificationServiceBase,
)
from app.modules.tenancy.module_toggles import is_module_enabled
from app.modules.tenancy.repository import TenancyRepository
from app.providers.notifications.base import (
    NotificationDispatchResult,
)


class DispatchMixin(NotificationServiceBase):
    def list_channels(self) -> list[NotificationChannelResponse]:
        return [
            NotificationChannelResponse(
                channel=descriptor.channel,
                display_name=descriptor.display_name,
                description=descriptor.description,
                configured=descriptor.configured,
                simulation_only=descriptor.simulation_only,
                target_hint=descriptor.target_hint,
                polling_supported=descriptor.polling_supported,
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
            response = self._to_dispatch_response(dispatched)
            results.append(response)

            if self._audit is not None:
                await self._audit.record_event(
                    tenant_id=tenant_id,
                    actor_user_id=actor_user_id,
                    action="notification_test",
                    entity_type="notification",
                    entity_id=channel,
                    module_key="notifications",
                    details={
                    "channel": response.channel,
                    "recipient": payload.recipient,
                    "subject": payload.subject,
                    "body": payload.body,
                    "delivery_status": response.status,
                    "delivery_stage": response.delivery_stage,
                    "simulation_only": response.simulation_only,
                    "delivered": response.delivered,
                    "provider_message": response.message,
                        "provider_reference": response.provider_reference,
                        "reconciliation_status": response.reconciliation_status,
                        "reconciliation_supported": response.reconciliation_supported,
                        "polling_supported": response.polling_supported,
                    },
                )

        if self._audit is not None and self._db is not None:
            await self._db.commit()

        return NotificationTestResponse(results=results)
    async def send_live_dispatch(
        self,
        *,
        tenant_id,
        actor_user_id,
        payload: NotificationDispatchRequest,
    ) -> NotificationDispatchResponse:
        provider = self._provider_map.get(payload.channel)
        if provider is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown notification channel: {payload.channel}",
            )

        descriptor = provider.describe()
        if descriptor.simulation_only:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Notification channel '{payload.channel}' only supports simulation in this sprint",
            )
        if not descriptor.configured:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Notification channel '{payload.channel}' is not configured for live delivery",
            )

        dispatched = await provider.send_message(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            recipient=payload.recipient,
            subject=payload.subject,
            body=payload.body,
        )
        response = self._to_dispatch_response(dispatched)

        if self._audit is not None:
            await self._audit.record_event(
                tenant_id=tenant_id,
                actor_user_id=actor_user_id,
                action="notification_dispatch",
                entity_type="notification",
                entity_id=payload.channel,
                module_key="notifications",
                details={
                    "channel": payload.channel,
                    "recipient": payload.recipient,
                    "subject": payload.subject,
                    "body": payload.body,
                    "delivery_status": response.status,
                    "delivery_stage": response.delivery_stage,
                    "simulation_only": response.simulation_only,
                    "delivered": response.delivered,
                    "provider_message": response.message,
                    "provider_reference": response.provider_reference,
                    "reconciliation_status": response.reconciliation_status,
                    "reconciliation_supported": response.reconciliation_supported,
                    "polling_supported": response.polling_supported,
                },
            )
            if self._db is not None:
                await self._db.commit()

        return response
    def _to_dispatch_response(self, dispatched: NotificationDispatchResult) -> NotificationDispatchResponse:
        return NotificationDispatchResponse(
            channel=dispatched.channel,
            status=dispatched.status,
            message=dispatched.message,
            delivered=dispatched.delivered,
            simulation_only=dispatched.simulation_only,
            delivery_stage=dispatched.delivery_stage,
            reconciliation_status=dispatched.reconciliation_status,
            reconciliation_supported=dispatched.reconciliation_supported,
            provider_reference=dispatched.provider_reference,
            polling_supported=dispatched.polling_supported,
        )
    async def _ensure_notifications_enabled(self, tenant_id) -> None:
        if self._db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Notification reconciliation is unavailable",
            )

        repo = TenancyRepository(self._db)
        tenant = await repo.get_tenant_by_id(tenant_id)
        if tenant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        raw_settings: dict[str, object] = {}
        if isinstance(tenant.settings_json, str) and tenant.settings_json.strip():
            try:
                raw_settings = json.loads(tenant.settings_json)
            except json.JSONDecodeError:
                raw_settings = {}

        if not is_module_enabled(raw_settings, "notifications"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The 'notifications' module is disabled for this organization",
            )
