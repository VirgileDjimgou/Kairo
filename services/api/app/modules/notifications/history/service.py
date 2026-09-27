from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from app.modules.audit.repository import AuditRepository
from app.modules.audit.schemas import AuditEventResponse
from app.modules.notifications.schemas import (
    NotificationHistoryEntry,
    NotificationHistoryResponse,
    NotificationHistorySummary,
)
from app.modules.notifications.service_base import (
    NotificationServiceBase,
    _RawNotificationAuditEvent,
)


class HistoryMixin(NotificationServiceBase):
    async def list_history(
        self,
        *,
        tenant_id,
        limit: int = 20,
        status_filter: str = "all",
        stale_only: bool = False,
    ) -> NotificationHistoryResponse:
        if self._audit is None:
            return NotificationHistoryResponse(
                items=[],
                summary=NotificationHistorySummary(
                    total=0,
                    pending=0,
                    delivered=0,
                    failed=0,
                    simulated=0,
                    stale_pending=0,
                ),
            )

        events = await self._audit.list_events(
            tenant_id,
            limit=max(limit * 10, 200),
            offset=0,
            module_key="notifications",
            entity_type="notification",
        )
        latest_reconciliation_by_key: dict[tuple[str, str], AuditEventResponse] = {}
        retried_provider_references: set[tuple[str, str]] = set()
        for event in events:
            channel = str(event.details.get("channel", event.entity_id or "unknown"))
            if event.action == "notification_reconciliation":
                provider_reference = event.details.get("provider_reference")
                if provider_reference:
                    latest_reconciliation_by_key.setdefault((channel, str(provider_reference)), event)
                continue
            if event.action == "notification_retry":
                source_provider_reference = event.details.get("source_provider_reference")
                if source_provider_reference:
                    retried_provider_references.add((channel, str(source_provider_reference)))

        history: list[NotificationHistoryEntry] = []
        summary = NotificationHistorySummary(
            total=0,
            pending=0,
            delivered=0,
            failed=0,
            simulated=0,
            stale_pending=0,
        )
        now = datetime.now(UTC)
        for event in events:
            if event.action not in {"notification_dispatch", "notification_test", "notification_retry"}:
                continue

            channel = str(event.details.get("channel", event.entity_id or "unknown"))
            provider_reference = (
                str(event.details["provider_reference"])
                if event.details.get("provider_reference") is not None
                else None
            )
            details = dict(event.details)
            created_at = event.created_at

            if event.action in {"notification_dispatch", "notification_retry"} and provider_reference is not None:
                reconciliation_event = latest_reconciliation_by_key.get((channel, provider_reference))
                if reconciliation_event is not None:
                    details.update(reconciliation_event.details)
                    created_at = reconciliation_event.created_at

            effective_created_at = (
                created_at.replace(tzinfo=UTC) if created_at.tzinfo is None else created_at.astimezone(UTC)
            )
            stale_minutes: int | None = None
            stale_pending = False
            if str(details.get("reconciliation_status", "not_applicable")) == "pending":
                delta = max(now - effective_created_at, timedelta())
                stale_minutes = int(delta.total_seconds() // 60)
                stale_pending = delta >= self.STALE_PENDING_AFTER

            retry_supported = False
            retry_eligible = False
            retry_source_provider_reference = (
                str(details["source_provider_reference"])
                if details.get("source_provider_reference") is not None
                else None
            )
            if event.action in {"notification_dispatch", "notification_retry"}:
                retry_supported = provider_reference is not None and not bool(details.get("simulation_only", False))
                retry_eligible = (
                    retry_supported
                    and str(details.get("delivery_stage", "unknown")) == "failed"
                    and provider_reference is not None
                    and (channel, provider_reference) not in retried_provider_references
                    and isinstance(details.get("subject"), (str, type(None)))
                    and isinstance(details.get("body"), str)
                    and bool(details.get("recipient"))
                )

            entry = NotificationHistoryEntry(
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
                provider_reference=provider_reference,
                polling_supported=bool(details.get("polling_supported", False)),
                retry_supported=retry_supported,
                retry_eligible=retry_eligible,
                retry_source_provider_reference=retry_source_provider_reference,
                stale_pending=stale_pending,
                stale_minutes=stale_minutes,
                created_at=created_at,
            )
            self._increment_history_summary(summary, entry)
            if not self._matches_history_filter(entry, status_filter):
                continue
            if stale_only and not entry.stale_pending:
                continue

            history.append(entry)

        history.sort(key=lambda item: item.created_at, reverse=True)
        return NotificationHistoryResponse(items=history[:limit], summary=summary)
    async def _list_raw_notification_events(
        self,
        *,
        tenant_id,
        action: str,
    ) -> list[_RawNotificationAuditEvent]:
        if self._db is None:
            return []

        rows = await AuditRepository(self._db).list_events(
            tenant_id,
            limit=200,
            offset=0,
            action=action,
            entity_type="notification",
            module_key="notifications",
        )
        events: list[_RawNotificationAuditEvent] = []
        for row in rows:
            try:
                details = json.loads(row.details_json)
            except json.JSONDecodeError:
                details = {}
            if not isinstance(details, dict):
                details = {}
            events.append(
                _RawNotificationAuditEvent(
                    id=row.id,
                    action=row.action,
                    entity_id=row.entity_id,
                    details=details,
                    created_at=row.created_at,
                )
            )
        return events
    def _increment_history_summary(
        self,
        summary: NotificationHistorySummary,
        entry: NotificationHistoryEntry,
    ) -> None:
        summary.total += 1
        if entry.reconciliation_status == "pending":
            summary.pending += 1
        elif entry.reconciliation_status == "delivered":
            summary.delivered += 1
        elif entry.reconciliation_status == "failed":
            summary.failed += 1
        elif entry.reconciliation_status == "not_applicable":
            summary.simulated += 1

        if entry.stale_pending:
            summary.stale_pending += 1
    def _matches_history_filter(
        self,
        entry: NotificationHistoryEntry,
        status_filter: str,
    ) -> bool:
        if status_filter == "all":
            return True
        if status_filter == "simulated":
            return entry.action == "notification_test" or entry.delivery_stage == "simulated"
        return entry.reconciliation_status == status_filter
