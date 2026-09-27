from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.service import AuditService
from app.modules.domain_events.events import (
    AGGREGATE_RECEIPT_DECLARATION,
    MODULE_CONTRIBUTIONS,
    RECEIPT_DECLARED,
    RECEIPT_HANDOVER_REMINDER_UPDATED,
    RECEIPT_HANDOVER_REPORTED,
    RECEIPT_PROCESSED_EVENT_TYPES,
    RECEIPT_RECEIVED_IN_TREASURY,
    RECEIPT_SUBMITTED,
    RECEIPT_UPDATED,
)
from app.modules.domain_events.models import DomainEvent
from app.modules.domain_events.registry import (
    DomainEventContext,
    DomainEventHandlerRegistry,
)

_RECEIPT_EVENT_ACTIONS: dict[str, str] = {
    RECEIPT_DECLARED: "receipt_declaration_created",
    RECEIPT_UPDATED: "receipt_declaration_updated",
    RECEIPT_SUBMITTED: "receipt_declaration_submitted",
    RECEIPT_HANDOVER_REPORTED: "receipt_handover_reported",
    RECEIPT_HANDOVER_REMINDER_UPDATED: "receipt_handover_reminder_updated",
    RECEIPT_RECEIVED_IN_TREASURY: "receipt_received_in_treasury",
}


class ReceiptAuditProjectionHandler:
    """Projects receipt domain events into the tenant audit trail.

    The projection is idempotent: the audit row carries a deduplication key derived
    from the immutable domain event id, so an outbox retry cannot duplicate history.
    """

    name = "audit.receipt_projection"

    def supports(self, event_type: str) -> bool:
        return event_type in _RECEIPT_EVENT_ACTIONS or event_type in RECEIPT_PROCESSED_EVENT_TYPES

    async def handle(
        self, db: AsyncSession, event: DomainEvent, context: DomainEventContext
    ) -> None:
        payload = event.payload
        action = _RECEIPT_EVENT_ACTIONS.get(event.event_type)
        if action is None:
            action = f"receipt_declaration_{payload.get('action', 'processed')}"
        details: Any = payload.get("audit_details", {})
        if not isinstance(details, dict):
            details = {}
        await AuditService(db).record_event(
            tenant_id=event.tenant_id,
            actor_user_id=event.actor_user_id,
            action=action,
            entity_type=AGGREGATE_RECEIPT_DECLARATION,
            entity_id=event.aggregate_id,
            module_key=MODULE_CONTRIBUTIONS,
            details=details,
            deduplication_key=f"domain-event:{event.id}",
        )


def register_audit_handlers(registry: DomainEventHandlerRegistry) -> None:
    registry.register(ReceiptAuditProjectionHandler())
