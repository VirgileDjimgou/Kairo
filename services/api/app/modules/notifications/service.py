from __future__ import annotations

import json

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.service import AuditService
from app.modules.notifications.schemas import (
    NotificationChannelResponse,
    NotificationDispatchRequest,
    NotificationDispatchResponse,
    NotificationHistoryEntry,
    NotificationReconciliationCallbackRequest,
    NotificationReconciliationCallbackResponse,
    NotificationReconciliationPollRequest,
    NotificationReconciliationPollResponse,
    NotificationTestRequest,
    NotificationTestResponse,
)
from app.modules.tenancy.module_toggles import is_module_enabled
from app.modules.tenancy.repository import TenancyRepository
from app.providers.notifications.base import (
    NotificationDeliveryStatusResult,
    NotificationProvider,
)


class NotificationService:
    def __init__(
        self,
        providers: list[NotificationProvider],
        db: AsyncSession | None = None,
        audit: AuditService | None = None,
    ) -> None:
        self._providers = providers
        self._provider_map = {provider.channel: provider for provider in providers}
        self._db = db
        self._audit = audit

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

    async def list_history(
        self,
        *,
        tenant_id,
        limit: int = 20,
    ) -> list[NotificationHistoryEntry]:
        if self._audit is None:
            return []

        events = await self._audit.list_events(
            tenant_id,
            limit=max(limit * 5, 100),
            offset=0,
            module_key="notifications",
            entity_type="notification",
        )
        latest_reconciliation_by_key: dict[tuple[str, str], object] = {}
        for event in events:
            if event.action != "notification_reconciliation":
                continue
            provider_reference = event.details.get("provider_reference")
            if not provider_reference:
                continue
            channel = str(event.details.get("channel", event.entity_id or "unknown"))
            latest_reconciliation_by_key.setdefault((channel, str(provider_reference)), event)

        history: list[NotificationHistoryEntry] = []
        for event in events:
            if event.action not in {"notification_dispatch", "notification_test"}:
                continue

            channel = str(event.details.get("channel", event.entity_id or "unknown"))
            provider_reference = (
                str(event.details["provider_reference"])
                if event.details.get("provider_reference") is not None
                else None
            )
            details = dict(event.details)
            created_at = event.created_at

            if event.action == "notification_dispatch" and provider_reference is not None:
                reconciliation_event = latest_reconciliation_by_key.get((channel, provider_reference))
                if reconciliation_event is not None:
                    details.update(reconciliation_event.details)
                    created_at = reconciliation_event.created_at

            history.append(
                NotificationHistoryEntry(
                    id=event.id,
                    action=event.action,
                    channel=channel,
                    recipient=str(details.get("recipient", "")),
                    status=str(details.get("delivery_status", "unknown")),
                    message=str(details.get("provider_message", "")),
                    delivered=bool(details.get("delivered", False)),
                    simulation_only=bool(details.get("simulation_only", False)),
                    delivery_stage=str(details.get("delivery_stage", "simulated")),
                    reconciliation_status=str(details.get("reconciliation_status", "not_applicable")),
                    reconciliation_supported=bool(details.get("reconciliation_supported", False)),
                    provider_reference=(
                        str(details["provider_reference"])
                        if details.get("provider_reference") is not None
                        else None
                    ),
                    polling_supported=bool(details.get("polling_supported", False)),
                    created_at=created_at,
                )
            )

        history.sort(key=lambda item: item.created_at, reverse=True)
        return history[:limit]

    async def record_provider_reconciliation(
        self,
        *,
        payload: NotificationReconciliationCallbackRequest,
    ) -> NotificationReconciliationCallbackResponse:
        if self._audit is None or self._db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Notification reconciliation is unavailable",
            )

        await self._ensure_notifications_enabled(payload.tenant_id)
        dispatch_event = await self._find_live_dispatch_event(
            tenant_id=payload.tenant_id,
            channel=payload.channel,
            provider_reference=payload.provider_reference,
        )
        if dispatch_event is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Matching live notification dispatch not found for reconciliation",
            )

        result = NotificationDeliveryStatusResult(
            delivery_stage=payload.delivery_stage,
            reconciliation_status=payload.delivery_stage,
            delivered=payload.delivery_stage == "delivered",
            provider_message=(
                payload.provider_message
                or str(dispatch_event.details.get("provider_message", "Provider reconciliation update received."))
            ),
            external_status=payload.external_status,
            terminal=True,
        )
        return await self._apply_reconciliation_update(
            tenant_id=payload.tenant_id,
            actor_user_id=None,
            channel=payload.channel,
            provider_reference=payload.provider_reference,
            recipient=str(dispatch_event.details.get("recipient", "")),
            result=result,
        )

    async def poll_provider_reconciliation(
        self,
        *,
        tenant_id,
        actor_user_id,
        payload: NotificationReconciliationPollRequest,
    ) -> NotificationReconciliationPollResponse:
        if self._audit is None or self._db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Notification reconciliation is unavailable",
            )

        await self._ensure_notifications_enabled(tenant_id)
        dispatch_event = await self._find_live_dispatch_event(
            tenant_id=tenant_id,
            channel=payload.channel,
            provider_reference=payload.provider_reference,
        )
        if dispatch_event is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Matching live notification dispatch not found for polling",
            )

        existing_reconciliation = await self._find_latest_reconciliation_event(
            tenant_id=tenant_id,
            channel=payload.channel,
            provider_reference=payload.provider_reference,
        )
        if existing_reconciliation is not None:
            existing_stage = str(existing_reconciliation.details.get("delivery_stage", "accepted"))
            return NotificationReconciliationPollResponse(
                channel=payload.channel,
                provider_reference=payload.provider_reference,
                delivery_stage=existing_stage,
                reconciliation_status=str(
                    existing_reconciliation.details.get("reconciliation_status", existing_stage)
                ),
                updated=False,
                provider_message=str(existing_reconciliation.details.get("provider_message", "Already reconciled.")),
                external_status=(
                    str(existing_reconciliation.details["external_status"])
                    if existing_reconciliation.details.get("external_status") is not None
                    else None
                ),
            )

        provider = self._provider_map.get(payload.channel)
        if provider is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown notification channel: {payload.channel}",
            )

        if not provider.describe().polling_supported:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Notification channel '{payload.channel}' does not support reconciliation polling",
            )

        polled_status = await provider.fetch_delivery_status(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            recipient=str(dispatch_event.details.get("recipient", "")),
            provider_reference=payload.provider_reference,
        )
        if polled_status is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Notification channel '{payload.channel}' could not return a reconciliation status",
            )

        if not polled_status.terminal:
            return NotificationReconciliationPollResponse(
                channel=payload.channel,
                provider_reference=payload.provider_reference,
                delivery_stage=polled_status.delivery_stage,
                reconciliation_status=polled_status.reconciliation_status,
                updated=False,
                provider_message=polled_status.provider_message,
                external_status=polled_status.external_status,
            )

        callback_response = await self._apply_reconciliation_update(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            channel=payload.channel,
            provider_reference=payload.provider_reference,
            recipient=str(dispatch_event.details.get("recipient", "")),
            result=polled_status,
        )
        return NotificationReconciliationPollResponse(
            channel=callback_response.channel,
            provider_reference=callback_response.provider_reference,
            delivery_stage=callback_response.delivery_stage,
            reconciliation_status=callback_response.reconciliation_status,
            updated=callback_response.updated,
            provider_message=polled_status.provider_message,
            external_status=polled_status.external_status,
        )

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

    def _to_dispatch_response(self, dispatched: object) -> NotificationDispatchResponse:
        return NotificationDispatchResponse(
            channel=getattr(dispatched, "channel"),
            status=getattr(dispatched, "status"),
            message=getattr(dispatched, "message"),
            delivered=getattr(dispatched, "delivered"),
            simulation_only=getattr(dispatched, "simulation_only"),
            delivery_stage=getattr(dispatched, "delivery_stage"),
            reconciliation_status=getattr(dispatched, "reconciliation_status"),
            reconciliation_supported=getattr(dispatched, "reconciliation_supported"),
            provider_reference=getattr(dispatched, "provider_reference"),
            polling_supported=getattr(dispatched, "polling_supported"),
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

    async def _find_live_dispatch_event(
        self,
        *,
        tenant_id,
        channel: str,
        provider_reference: str,
    ):
        if self._audit is None:
            return None

        events = await self._audit.list_events(
            tenant_id,
            limit=200,
            offset=0,
            action="notification_dispatch",
            entity_type="notification",
            module_key="notifications",
        )
        for event in events:
            if str(event.details.get("channel", event.entity_id or "")) != channel:
                continue
            if str(event.details.get("provider_reference") or "") != provider_reference:
                continue
            if not bool(event.details.get("reconciliation_supported", False)):
                continue
            return event
        return None

    async def _find_latest_reconciliation_event(
        self,
        *,
        tenant_id,
        channel: str,
        provider_reference: str,
    ):
        if self._audit is None:
            return None

        events = await self._audit.list_events(
            tenant_id,
            limit=200,
            offset=0,
            action="notification_reconciliation",
            entity_type="notification",
            module_key="notifications",
        )
        for event in events:
            if str(event.details.get("channel", event.entity_id or "")) != channel:
                continue
            if str(event.details.get("provider_reference") or "") != provider_reference:
                continue
            return event
        return None

    async def _apply_reconciliation_update(
        self,
        *,
        tenant_id,
        actor_user_id,
        channel: str,
        provider_reference: str,
        recipient: str,
        result: NotificationDeliveryStatusResult,
    ) -> NotificationReconciliationCallbackResponse:
        if self._audit is None or self._db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Notification reconciliation is unavailable",
            )

        existing_reconciliation = await self._find_latest_reconciliation_event(
            tenant_id=tenant_id,
            channel=channel,
            provider_reference=provider_reference,
        )
        if existing_reconciliation is not None:
            existing_stage = str(existing_reconciliation.details.get("delivery_stage", "accepted"))
            if existing_stage == result.delivery_stage:
                return NotificationReconciliationCallbackResponse(
                    channel=channel,
                    provider_reference=provider_reference,
                    delivery_stage=existing_stage,
                    reconciliation_status=str(
                        existing_reconciliation.details.get("reconciliation_status", existing_stage)
                    ),
                    updated=False,
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A final reconciliation state is already recorded for this notification dispatch",
            )

        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="notification_reconciliation",
            entity_type="notification",
            entity_id=channel,
            module_key="notifications",
            details={
                "channel": channel,
                "recipient": recipient,
                "delivery_status": result.delivery_stage,
                "delivery_stage": result.delivery_stage,
                "simulation_only": False,
                "delivered": result.delivered,
                "provider_message": result.provider_message,
                "provider_reference": provider_reference,
                "reconciliation_status": result.reconciliation_status,
                "reconciliation_supported": True,
                "external_status": result.external_status,
            },
        )
        await self._db.commit()
        return NotificationReconciliationCallbackResponse(
            channel=channel,
            provider_reference=provider_reference,
            delivery_stage=result.delivery_stage,
            reconciliation_status=result.reconciliation_status,
            updated=True,
        )
