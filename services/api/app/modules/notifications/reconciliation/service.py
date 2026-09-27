from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.notifications.schemas import (
    NotificationReconciliationCallbackRequest,
    NotificationReconciliationCallbackResponse,
    NotificationReconciliationPollRequest,
    NotificationReconciliationPollResponse,
    NotificationRetryRequest,
    NotificationRetryResponse,
)
from app.modules.notifications.service_base import (
    NotificationServiceBase,
)
from app.providers.notifications.base import (
    NotificationDeliveryStatusResult,
)


class ReconciliationMixin(NotificationServiceBase):
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
    async def retry_failed_dispatch(
        self,
        *,
        tenant_id,
        actor_user_id,
        payload: NotificationRetryRequest,
    ) -> NotificationRetryResponse:
        if self._audit is None or self._db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Notification retry is unavailable",
            )

        await self._ensure_notifications_enabled(tenant_id)
        provider = self._provider_map.get(payload.channel)
        if provider is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown notification channel: {payload.channel}",
            )

        descriptor = provider.describe()
        if descriptor.simulation_only or not descriptor.configured:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Notification channel '{payload.channel}' is not eligible for retry",
            )

        source_event = await self._find_live_dispatch_event(
            tenant_id=tenant_id,
            channel=payload.channel,
            provider_reference=payload.provider_reference,
        )
        if source_event is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Matching notification dispatch not found for retry",
            )

        source_details = dict(source_event.details)
        effective_details = dict(source_details)
        reconciliation_event = await self._find_latest_reconciliation_event(
            tenant_id=tenant_id,
            channel=payload.channel,
            provider_reference=payload.provider_reference,
        )
        if reconciliation_event is not None:
            effective_details.update(reconciliation_event.details)

        if str(effective_details.get("delivery_stage", "accepted")) != "failed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only failed notification deliveries can be retried",
            )

        existing_retry = await self._find_retry_event(
            tenant_id=tenant_id,
            channel=payload.channel,
            source_provider_reference=payload.provider_reference,
        )
        if existing_retry is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This notification delivery has already been retried",
            )

        recipient = source_details.get("recipient")
        body = source_details.get("body")
        if not isinstance(recipient, str) or not recipient or not isinstance(body, str) or not body:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The original notification payload is incomplete and cannot be retried safely",
            )
        subject = source_details.get("subject")
        if subject is not None and not isinstance(subject, str):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The original notification payload is incomplete and cannot be retried safely",
            )

        dispatched = await provider.send_message(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            recipient=recipient,
            subject=subject,
            body=body,
        )
        response = self._to_dispatch_response(dispatched)
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="notification_retry",
            entity_type="notification",
            entity_id=payload.channel,
            module_key="notifications",
            details={
                "channel": payload.channel,
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "delivery_status": response.status,
                "delivery_stage": response.delivery_stage,
                "simulation_only": response.simulation_only,
                "delivered": response.delivered,
                "provider_message": response.message,
                "provider_reference": response.provider_reference,
                "source_provider_reference": payload.provider_reference,
                "reconciliation_status": response.reconciliation_status,
                "reconciliation_supported": response.reconciliation_supported,
                "polling_supported": response.polling_supported,
            },
        )
        await self._db.commit()
        return NotificationRetryResponse(
            source_provider_reference=payload.provider_reference,
            dispatch=response,
        )
    async def _find_live_dispatch_event(
        self,
        *,
        tenant_id,
        channel: str,
        provider_reference: str,
    ):
        if self._db is None:
            return None

        events = await self._list_raw_notification_events(
            tenant_id=tenant_id,
            action="notification_dispatch",
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
        if self._db is None:
            return None

        events = await self._list_raw_notification_events(
            tenant_id=tenant_id,
            action="notification_reconciliation",
        )
        for event in events:
            if str(event.details.get("channel", event.entity_id or "")) != channel:
                continue
            if str(event.details.get("provider_reference") or "") != provider_reference:
                continue
            return event
        return None
    async def _find_retry_event(
        self,
        *,
        tenant_id,
        channel: str,
        source_provider_reference: str,
    ):
        if self._db is None:
            return None

        events = await self._list_raw_notification_events(
            tenant_id=tenant_id,
            action="notification_retry",
        )
        for event in events:
            if str(event.details.get("channel", event.entity_id or "")) != channel:
                continue
            if str(event.details.get("source_provider_reference") or "") != source_provider_reference:
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
