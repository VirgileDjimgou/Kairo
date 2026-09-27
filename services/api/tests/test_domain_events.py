"""Domain event outbox coverage for representative receipt workflows."""

from __future__ import annotations

import inspect
import uuid

import pytest
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditEvent
from app.modules.audit.service import AuditService
from app.modules.contributions.models import ContributionRecord, PaymentRecord
from app.modules.domain_events.events import (
    AGGREGATE_RECEIPT_DECLARATION,
    RECEIPT_PROCESSED_EVENT_TYPES,
)
from app.modules.domain_events.models import DomainEvent
from app.modules.domain_events.registry import default_registry
from app.modules.domain_events.service import DomainEventService
from app.modules.notifications.user_models import NotificationOutboxEvent, UserNotification
from app.modules.notifications.user_service import UserNotificationService


async def _validated_receipt_context(
    client: AsyncClient, db_session: AsyncSession
) -> dict:
    admin = await create_tenant_with_user(db_session, f"dom-ev-{uuid.uuid4().hex[:6]}")
    declarant = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"vice.dom-{uuid.uuid4().hex[:6]}@test.org",
        password="VicePass123!",
        display_name="Vice Domain",
        role_code="vice_president",
        profile_type="staff",
    )
    treasurer = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"treasurer.dom-{uuid.uuid4().hex[:6]}@test.org",
        password="TreasurerPass123!",
        display_name="Treasurer Domain",
        role_code="treasurer",
        profile_type="staff",
    )
    member = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"member.dom-{uuid.uuid4().hex[:6]}@test.org",
        password="MemberPass123!",
        display_name="Member Domain",
        role_code="member",
        profile_type="member",
        member_code=f"DOM-{uuid.uuid4().hex[:6]}",
    )
    await db_session.commit()

    admin_token = await login(client, admin["user"].email, admin["password"], admin["tenant"].slug)
    declarant_token = await login(
        client, declarant["user"].email, declarant["password"], admin["tenant"].slug
    )
    treasurer_token = await login(
        client, treasurer["user"].email, treasurer["password"], admin["tenant"].slug
    )

    contribution = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": str(member["profile"].id),
            "year": 2026,
            "expected_amount": "60.00",
            "paid_amount": "0.00",
            "currency": "EUR",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert contribution.status_code == 201, contribution.text

    declaration = await client.post(
        "/api/v1/contributions/receipt-declarations",
        json={
            "membership_profile_id": str(member["profile"].id),
            "amount": "20.00",
            "currency": "EUR",
            "payment_method": "cash",
        },
        headers={"Authorization": f"Bearer {declarant_token}"},
    )
    assert declaration.status_code == 201, declaration.text
    declaration_id = declaration.json()["id"]

    submitted = await client.post(
        f"/api/v1/contributions/receipt-declarations/{declaration_id}/submit",
        headers={"Authorization": f"Bearer {declarant_token}"},
    )
    assert submitted.status_code == 200, submitted.text

    processed = await client.post(
        f"/api/v1/contributions/receipt-declarations/{declaration_id}/process",
        json={"action": "validated", "contribution_record_id": contribution.json()["id"]},
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )
    assert processed.status_code == 200, processed.text
    assert processed.json()["cash_handover_status"] == "pending_handover"

    return {
        "tenant_id": admin["tenant"].id,
        "declarant_user_id": declarant["user"].id,
        "treasurer_user_id": treasurer["user"].id,
        "member_user_id": member["user"].id,
        "declaration_id": declaration_id,
        "contribution_id": contribution.json()["id"],
    }


@pytest.mark.asyncio
async def test_receipt_validation_emits_domain_event_consumed_by_audit_and_notifications(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await _validated_receipt_context(client, db_session)
    tenant_id = context["tenant_id"]

    events = list(
        (
            await db_session.execute(
                select(DomainEvent).where(
                    DomainEvent.tenant_id == tenant_id,
                    DomainEvent.event_type == "finance.receipt_validated",
                )
            )
        ).scalars()
    )
    assert len(events) == 1
    event = events[0]
    assert event.status == "completed"
    assert event.attempts == 1
    assert event.aggregate_type == AGGREGATE_RECEIPT_DECLARATION
    assert event.aggregate_id == context["declaration_id"]
    assert event.deduplication_key == (
        f"receipt-processed:{context['declaration_id']}:validated"
    )
    assert event.applied_handlers == ["audit.receipt_projection", "notifications.receipt_inbox"]
    assert event.occurred_at is not None
    assert event.processed_at is not None
    assert event.correlation_id is not None

    declaration_event = await db_session.scalar(
        select(DomainEvent).where(
            DomainEvent.tenant_id == tenant_id,
            DomainEvent.event_type == "finance.receipt_declared",
        )
    )
    assert declaration_event is not None
    assert declaration_event.actor_user_id is not None

    audit = await db_session.scalar(
        select(AuditEvent).where(
            AuditEvent.tenant_id == tenant_id,
            AuditEvent.action == "receipt_declaration_validated",
            AuditEvent.entity_id == context["declaration_id"],
        )
    )
    assert audit is not None
    assert audit.deduplication_key == f"domain-event:{event.id}"

    outbox = await db_session.scalar(
        select(NotificationOutboxEvent).where(
            NotificationOutboxEvent.tenant_id == tenant_id,
            NotificationOutboxEvent.deduplication_key
            == f"receipt-processed:{context['declaration_id']}:validated",
        )
    )
    assert outbox is not None
    assert outbox.event_type == "finance.receipt_validated"

    await UserNotificationService(db_session).process_outbox()
    validated_recipients = set(
        (
            await db_session.execute(
                select(UserNotification.recipient_user_id).where(
                    UserNotification.tenant_id == tenant_id,
                    UserNotification.event_type == "finance.receipt_validated",
                )
            )
        )
        .scalars()
        .all()
    )
    assert validated_recipients == {context["declarant_user_id"], context["member_user_id"]}

    declared_recipients = set(
        (
            await db_session.execute(
                select(UserNotification.recipient_user_id).where(
                    UserNotification.tenant_id == tenant_id,
                    UserNotification.event_type == "finance.receipt_declared",
                )
            )
        )
        .scalars()
        .all()
    )
    assert declared_recipients == {context["treasurer_user_id"]}

    isolated = await db_session.scalar(
        select(func.count(DomainEvent.id)).where(DomainEvent.tenant_id == uuid.uuid4())
    )
    assert isolated == 0


@pytest.mark.asyncio
async def test_domain_event_outbox_retry_is_idempotent_and_does_not_duplicate_finance(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await _validated_receipt_context(client, db_session)
    tenant_id = context["tenant_id"]

    event = await db_session.scalar(
        select(DomainEvent).where(
            DomainEvent.tenant_id == tenant_id,
            DomainEvent.event_type == "finance.receipt_validated",
        )
    )
    assert event is not None
    contribution = await db_session.get(ContributionRecord, uuid.UUID(context["contribution_id"]))
    assert contribution is not None

    async def tenant_counts() -> tuple[int, int, int]:
        audit_count = await db_session.scalar(
            select(func.count(AuditEvent.id)).where(AuditEvent.tenant_id == tenant_id)
        )
        outbox_count = await db_session.scalar(
            select(func.count(NotificationOutboxEvent.id)).where(
                NotificationOutboxEvent.tenant_id == tenant_id
            )
        )
        payment_count = await db_session.scalar(
            select(func.count(PaymentRecord.id)).where(PaymentRecord.tenant_id == tenant_id)
        )
        return int(audit_count or 0), int(outbox_count or 0), int(payment_count or 0)

    before = await tenant_counts()
    paid_before = contribution.paid_amount

    event.status = "pending"
    event.applied_handlers_json = "[]"
    event.processed_at = None
    event.attempts = 0
    await db_session.commit()

    completed = await DomainEventService(db_session).process_pending()
    assert completed == 1
    await db_session.refresh(event)

    assert event.status == "completed"
    assert event.applied_handlers == ["audit.receipt_projection", "notifications.receipt_inbox"]
    assert await tenant_counts() == before

    await db_session.refresh(contribution)
    assert contribution.paid_amount == paid_before

    duplicate = await DomainEventService(db_session).publish(
        tenant_id=tenant_id,
        event_type="finance.receipt_validated",
        aggregate_type=AGGREGATE_RECEIPT_DECLARATION,
        aggregate_id=context["declaration_id"],
        deduplication_key=f"receipt-processed:{context['declaration_id']}:validated",
        payload={},
        actor_user_id=context["treasurer_user_id"],
    )
    assert duplicate.id == event.id
    assert await tenant_counts() == before


@pytest.mark.asyncio
async def test_audit_projection_deduplication_key_is_idempotent(
    db_session: AsyncSession,
) -> None:
    tenant = await create_tenant_with_user(db_session, f"audit-dedup-{uuid.uuid4().hex[:6]}")
    await db_session.commit()
    service = AuditService(db_session)

    first = await service.record_event(
        tenant_id=tenant["tenant"].id,
        actor_user_id=None,
        action="receipt_declaration_validated",
        entity_type="contribution_receipt_declaration",
        entity_id=uuid.uuid4(),
        module_key="contributions",
        details={"source": "domain-event"},
        deduplication_key="domain-event:fixed-key",
    )
    second = await service.record_event(
        tenant_id=tenant["tenant"].id,
        actor_user_id=None,
        action="receipt_declaration_validated",
        entity_type="contribution_receipt_declaration",
        entity_id=uuid.uuid4(),
        module_key="contributions",
        details={"source": "domain-event"},
        deduplication_key="domain-event:fixed-key",
    )
    assert first.id == second.id
    count = await db_session.scalar(
        select(func.count(AuditEvent.id)).where(
            AuditEvent.tenant_id == tenant["tenant"].id,
            AuditEvent.deduplication_key == "domain-event:fixed-key",
        )
    )
    assert count == 1


@pytest.mark.asyncio
async def test_domain_event_deduplication_is_scoped_per_tenant(
    db_session: AsyncSession,
) -> None:
    first = await create_tenant_with_user(db_session, f"dom-dedup-a-{uuid.uuid4().hex[:6]}")
    second = await create_tenant_with_user(db_session, f"dom-dedup-b-{uuid.uuid4().hex[:6]}")
    await db_session.commit()
    service = DomainEventService(db_session)
    aggregate_id = uuid.uuid4()

    first_event = await service.publish(
        tenant_id=first["tenant"].id,
        event_type="finance.receipt_declared",
        aggregate_type=AGGREGATE_RECEIPT_DECLARATION,
        aggregate_id=aggregate_id,
        deduplication_key="same-key",
        payload={},
        dispatch=False,
    )
    second_event = await service.publish(
        tenant_id=second["tenant"].id,
        event_type="finance.receipt_declared",
        aggregate_type=AGGREGATE_RECEIPT_DECLARATION,
        aggregate_id=aggregate_id,
        deduplication_key="same-key",
        payload={},
        dispatch=False,
    )
    assert first_event.id != second_event.id
    for tenant in (first, second):
        count = await db_session.scalar(
            select(func.count(DomainEvent.id)).where(
                DomainEvent.tenant_id == tenant["tenant"].id
            )
        )
        assert count == 1
    await db_session.commit()


def test_receipt_workflow_modules_depend_on_events_not_transport() -> None:
    from app.modules.finance.custody import service as custody_service
    from app.modules.finance.receipts import service as receipts_service

    source = inspect.getsource(receipts_service) + inspect.getsource(custody_service)
    assert "AuditService" not in source
    assert "UserNotificationService" not in source
    assert "finance.notifications" not in source
    assert "domain_events" in source

    names = default_registry().handler_names()
    assert "audit.receipt_projection" in names
    assert "notifications.receipt_inbox" in names
    assert "notifications.custody_notice" in names

    assert "finance.receipt_validated" in RECEIPT_PROCESSED_EVENT_TYPES
    assert "finance.receipt_rejected" in RECEIPT_PROCESSED_EVENT_TYPES
