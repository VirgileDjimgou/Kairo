from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.service import AuditService
from app.modules.contributions.models import ContributionReceiptDeclaration
from app.modules.identity.repository import UserRepository
from app.modules.membership.repository import MembershipRepository
from app.modules.notifications.user_service import UserNotificationService
from app.providers.notifications.base import NotificationProvider


async def notify_receipt_declared(
    db: AsyncSession,
    tenant_id: UUID,
    *,
    record: ContributionReceiptDeclaration,
) -> None:
    notification_service = UserNotificationService(db)
    treasurers = await notification_service.users_with_roles(tenant_id, ["treasurer", "principal_admin"])
    await notification_service.enqueue(
        tenant_id=tenant_id,
        event_type="finance.receipt_declared",
        recipients=treasurers,
        category="finance",
        target_path="/finance",
        deduplication_key=f"receipt-declared:{record.id}",
        metadata={"income_type": record.income_type},
        priority="high",
    )


async def notify_receipt_processed(
    db: AsyncSession,
    tenant_id: UUID,
    *,
    record: ContributionReceiptDeclaration,
    updated: ContributionReceiptDeclaration,
    action: str,
) -> None:
    notification_service = UserNotificationService(db)
    recipients = [record.declarant_user_id]
    if record.membership_profile_id is not None:
        profile = await MembershipRepository(db).get_by_id(tenant_id, record.membership_profile_id)
        if profile is not None and profile.user_id is not None:
            recipients.append(profile.user_id)
    await notification_service.enqueue(
        tenant_id=tenant_id,
        event_type=f"finance.receipt_{action}",
        recipients=recipients,
        category="finance",
        target_path="/finance",
        deduplication_key=f"receipt-processed:{updated.id}:{action}",
        metadata={"income_type": updated.income_type},
        priority="high" if action in {"validated", "rejected"} else "normal",
    )


async def dispatch_custody_notice(
    db: AsyncSession,
    tenant_id: UUID,
    *,
    providers: list[NotificationProvider],
    record: ContributionReceiptDeclaration,
    actor_user_id: UUID,
    subject: str,
    body: str,
    audit_action: str,
) -> None:
    recipients: set[str] = set()
    user_repo = UserRepository(db)
    declarant = await user_repo.get_by_id(record.declarant_user_id)
    if declarant and declarant.email:
        recipients.add(declarant.email)
    if record.membership_profile_id is not None:
        profile = await MembershipRepository(db).get_by_id(tenant_id, record.membership_profile_id)
        if profile and profile.user_id and profile.user_id != record.declarant_user_id:
            member_user = await user_repo.get_by_id(profile.user_id)
            if member_user and member_user.email:
                recipients.add(member_user.email)
    provider = next((item for item in providers if getattr(item, "channel", "") == "email"), None)
    delivery_states: list[dict[str, str]] = []
    for recipient in recipients:
        if provider is None:
            delivery_states.append({"recipient": recipient, "status": "not_configured"})
            continue
        try:
            result = await provider.send_message(
                tenant_id=tenant_id, actor_user_id=actor_user_id, recipient=recipient, subject=subject, body=body,
            )
            delivery_states.append({"recipient": recipient, "status": result.status})
        except Exception:  # Notifications must not undo a valid treasury action.
            delivery_states.append({"recipient": recipient, "status": "failed"})
    await AuditService(db).record_event(
        tenant_id=tenant_id, actor_user_id=actor_user_id, action=audit_action,
        entity_type="contribution_receipt_declaration", entity_id=record.id,
        module_key="contributions", details={"recipients": delivery_states},
    )
