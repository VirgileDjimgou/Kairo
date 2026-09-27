from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.service import AuditService
from app.modules.domain_events.events import (
    AGGREGATE_RECEIPT_DECLARATION,
    EXPENSE_RECORDED,
    MODULE_CONTRIBUTIONS,
    PAYMENT_RECORDED,
    RECEIPT_DECLARED,
    RECEIPT_HANDOVER_REMINDER_UPDATED,
    RECEIPT_PROCESSED_EVENT_TYPES,
    RECEIPT_RECEIVED_IN_TREASURY,
)
from app.modules.domain_events.models import DomainEvent
from app.modules.domain_events.registry import (
    DomainEventContext,
    DomainEventHandlerRegistry,
)
from app.modules.identity.repository import UserRepository
from app.modules.membership.repository import MembershipRepository
from app.modules.notifications.user_service import UserNotificationService

_RECEIPT_TREASURER_ROLES = ("treasurer", "principal_admin")


class ReceiptInboxNotificationHandler:
    """Resolves recipients for receipt events and submits notification intents.

    The handler owns recipient policy; the emitting business module only publishes
    the fact. Idempotency comes from the canonical notification policy, so an
    outbox retry cannot duplicate inbox items.
    """

    name = "notifications.receipt_inbox"

    def supports(self, event_type: str) -> bool:
        return event_type == RECEIPT_DECLARED or event_type in RECEIPT_PROCESSED_EVENT_TYPES

    async def handle(
        self, db: AsyncSession, event: DomainEvent, context: DomainEventContext
    ) -> None:
        payload = event.payload
        service = UserNotificationService(db)

        if event.event_type == RECEIPT_DECLARED:
            recipients = await service.users_with_roles(event.tenant_id, _RECEIPT_TREASURER_ROLES)
            await service.notify(
                tenant_id=event.tenant_id,
                event_type="finance.receipt_declared",
                recipients=recipients,
                category="finance",
                target_path="/finance",
                deduplication_key=f"receipt-declared:{event.aggregate_id}",
                metadata={"income_type": payload.get("income_type")},
                priority="high",
                event_id=event.id,
                correlation_id=event.correlation_id,
            )
            return

        action = str(payload.get("action", ""))
        recipients = await self._receipt_recipients(db, event, payload)
        await service.notify(
            tenant_id=event.tenant_id,
            event_type=f"finance.receipt_{action}",
            recipients=recipients,
            category="finance",
            target_path="/finance",
            deduplication_key=f"receipt-processed:{event.aggregate_id}:{action}",
            metadata={"income_type": payload.get("income_type")},
            priority="high" if action in {"validated", "rejected"} else "normal",
            event_id=event.id,
            correlation_id=event.correlation_id,
        )

    async def _receipt_recipients(
        self, db: AsyncSession, event: DomainEvent, payload: dict
    ) -> list[UUID]:
        recipients: list[UUID] = []
        declarant = payload.get("declarant_user_id")
        if declarant:
            recipients.append(UUID(str(declarant)))
        profile_id = payload.get("membership_profile_id")
        if profile_id:
            profile = await MembershipRepository(db).get_by_id(
                event.tenant_id, UUID(str(profile_id))
            )
            if profile is not None and profile.user_id is not None:
                recipients.append(profile.user_id)
        return list(dict.fromkeys(recipients))


class CustodyNoticeHandler:
    """Sends the custody email notice, records its outcome and refreshes the inbox."""

    name = "notifications.custody_notice"

    def supports(self, event_type: str) -> bool:
        return event_type in {RECEIPT_HANDOVER_REMINDER_UPDATED, RECEIPT_RECEIVED_IN_TREASURY}

    async def handle(
        self, db: AsyncSession, event: DomainEvent, context: DomainEventContext
    ) -> None:
        payload = event.payload
        user_ids = await self._notice_user_ids(db, event, payload)
        if event.event_type == RECEIPT_HANDOVER_REMINDER_UPDATED:
            subject = "Kairo — délai de remise mis à jour"
            body = (
                "Le délai de remise en caisse pour l'encaissement de "
                f"{payload.get('amount')} {payload.get('currency')} a été fixé à "
                f"{payload.get('reminder_days')} jour(s)."
            )
            audit_action = "receipt_handover_reminder_notice"
        else:
            subject = "Kairo — encaissement clôturé"
            body = (
                "Le trésorier a confirmé la réception en caisse de "
                f"{payload.get('amount')} {payload.get('currency')}. L'opération est terminée."
            )
            audit_action = "receipt_treasury_closure_notice"
            await UserNotificationService(db).notify(
                tenant_id=event.tenant_id,
                event_type="finance.receipt_received_in_treasury",
                recipients=user_ids,
                category="finance",
                target_path="/finance",
                deduplication_key=f"receipt-received-in-treasury:{event.aggregate_id}",
                metadata={"amount": payload.get("amount"), "currency": payload.get("currency")},
                priority="normal",
                event_id=event.id,
                correlation_id=event.correlation_id,
            )

        provider = next(
            (
                item
                for item in context.notification_providers
                if getattr(item, "channel", "") == "email"
            ),
            None,
        )
        user_repo = UserRepository(db)
        delivery_states: list[dict[str, str]] = []
        for user_id in user_ids:
            user = await user_repo.get_by_id(user_id)
            if user is None or not user.email:
                continue
            if provider is None:
                delivery_states.append({"recipient": user.email, "status": "not_configured"})
                continue
            try:
                result = await provider.send_message(
                    tenant_id=event.tenant_id,
                    actor_user_id=event.actor_user_id,
                    recipient=user.email,
                    subject=subject,
                    body=body,
                )
                delivery_states.append({"recipient": user.email, "status": result.status})
            except Exception:
                delivery_states.append({"recipient": user.email, "status": "failed"})

        await AuditService(db).record_event(
            tenant_id=event.tenant_id,
            actor_user_id=event.actor_user_id,
            action=audit_action,
            entity_type=AGGREGATE_RECEIPT_DECLARATION,
            entity_id=event.aggregate_id,
            module_key=MODULE_CONTRIBUTIONS,
            details={"recipients": delivery_states},
            deduplication_key=f"domain-event:{event.id}:notice",
        )

    async def _notice_user_ids(
        self, db: AsyncSession, event: DomainEvent, payload: dict
    ) -> list[UUID]:
        user_ids: list[UUID] = []
        declarant_id: UUID | None = None
        declarant_raw = payload.get("declarant_user_id")
        if declarant_raw:
            declarant_id = UUID(str(declarant_raw))
            user_ids.append(declarant_id)
        profile_id = payload.get("membership_profile_id")
        if profile_id:
            profile = await MembershipRepository(db).get_by_id(
                event.tenant_id, UUID(str(profile_id))
            )
            if profile is not None and profile.user_id is not None:
                user_ids.append(profile.user_id)
        return list(dict.fromkeys(user_ids))


class FinanceRecordsNotificationHandler:
    """Inbox hints for recorded payments (self) and expenses (auditor oversight)."""

    name = "notifications.finance_records"

    def supports(self, event_type: str) -> bool:
        return event_type in {PAYMENT_RECORDED, EXPENSE_RECORDED}

    async def handle(
        self, db: AsyncSession, event: DomainEvent, context: DomainEventContext
    ) -> None:
        payload = event.payload
        service = UserNotificationService(db)
        if event.event_type == PAYMENT_RECORDED:
            profile_id = payload.get("membership_profile_id")
            if not profile_id:
                return
            profile = await MembershipRepository(db).get_by_id(
                event.tenant_id, UUID(str(profile_id))
            )
            if profile is None or profile.user_id is None:
                return
            await service.notify(
                tenant_id=event.tenant_id,
                event_type="finance.payment_recorded",
                recipients=[profile.user_id],
                category="finance",
                target_path="/finance",
                deduplication_key=f"payment-recorded:{event.aggregate_id}",
                metadata={
                    "amount": payload.get("amount"),
                    "currency": payload.get("currency"),
                },
                priority="normal",
                event_id=event.id,
                correlation_id=event.correlation_id,
            )
            return

        recipients = await service.users_with_roles(event.tenant_id, ("auditor",))
        await service.notify(
            tenant_id=event.tenant_id,
            event_type="finance.expense_recorded",
            recipients=recipients,
            category="finance",
            target_path="/finance",
            deduplication_key=f"expense-recorded:{event.aggregate_id}",
            metadata={
                "category": payload.get("category"),
                "amount": payload.get("amount"),
                "currency": payload.get("currency"),
            },
            priority="normal",
            event_id=event.id,
            correlation_id=event.correlation_id,
        )


def register_notification_handlers(registry: DomainEventHandlerRegistry) -> None:
    registry.register(ReceiptInboxNotificationHandler())
    registry.register(CustodyNoticeHandler())
    registry.register(FinanceRecordsNotificationHandler())
