"""Background follow-up for validated receipts that have not reached the treasury."""

import asyncio
from datetime import UTC, datetime

from sqlalchemy import or_, select

from app.db import models as _all_models  # noqa: F401
from app.db.session import async_session_factory
from app.modules.audit.service import AuditService
from app.modules.contributions.models import CashHandoverStatus, ContributionReceiptDeclaration
from app.modules.identity.repository import UserRepository
from app.providers.notifications.placeholders import EmailNotificationProvider
from app.worker.celery_app import celery_app


@celery_app.task(name="contributions.send_due_receipt_handover_reminders")
def send_due_receipt_handover_reminders() -> int:
    return asyncio.run(_send_due_reminders())


async def _send_due_reminders() -> int:
    now = datetime.now(UTC)
    sent_count = 0
    async with async_session_factory() as db:
        result = await db.execute(
            select(ContributionReceiptDeclaration).where(
                ContributionReceiptDeclaration.cash_handover_status.in_(
                    [CashHandoverStatus.pending_handover.value, CashHandoverStatus.handover_reported.value]
                ),
                ContributionReceiptDeclaration.handover_due_at.is_not(None),
                ContributionReceiptDeclaration.handover_due_at <= now,
                ContributionReceiptDeclaration.handover_reminder_sent_at.is_(None),
            )
        )
        provider = EmailNotificationProvider()
        users = UserRepository(db)
        audit = AuditService(db)
        for receipt in result.scalars().all():
            declarant = await users.get_by_id(receipt.declarant_user_id)
            delivery_status = "skipped"
            if declarant and declarant.email:
                dispatched = await provider.send_message(
                    tenant_id=receipt.tenant_id,
                    actor_user_id=None,
                    recipient=declarant.email,
                    subject="Kairo — rappel de remise en caisse",
                    body=(
                        f"La remise en caisse de {receipt.amount} {receipt.currency} est toujours ouverte. "
                        "Merci de la remettre au trésorier ou de signaler le virement."
                    ),
                )
                delivery_status = dispatched.status
            receipt.handover_reminder_sent_at = now
            await audit.record_event(
                tenant_id=receipt.tenant_id,
                actor_user_id=None,
                action="receipt_handover_reminder_due",
                entity_type="contribution_receipt_declaration",
                entity_id=receipt.id,
                module_key="contributions",
                details={"status": delivery_status, "due_at": receipt.handover_due_at.isoformat()},
            )
            sent_count += 1
        await db.commit()
    return sent_count
