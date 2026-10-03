"""Canonical deep-link allowlist, envelope and privacy-safe push payloads."""

from __future__ import annotations

import json

import pytest
import pytest_asyncio
from fakes import FakeFirebasePushProvider, FakeWebPushProvider
from helpers import create_tenant_with_user
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.deep_links import resolve_target_path
from app.modules.notifications.user_models import (
    FirebasePushSubscription,
    NotificationDevice,
    NotificationDeviceProfile,
    NotificationOutboxEvent,
    UserNotification,
    WebPushSubscription,
)
from app.modules.notifications.user_service import UserNotificationService

WEB_ENDPOINT = "https://push.example.org/deep-links/web"
INSTALLATION = "installation-deep-links-0001"

REPRESENTATIVE_CASES = [
    ("finance.payment_recorded", "finance", "/finance"),
    ("finance.receipt_declared", "finance", "/finance"),
    ("finance.receipt_validated", "finance", "/finance"),
    ("finance.receipt_rejected", "finance", "/finance"),
    ("finance.receipt_received_in_treasury", "finance", "/finance"),
    ("finance.expense_recorded", "finance", "/finance"),
    ("announcement.published", "announcements", "/announcements"),
    ("event.published", "events", "/events"),
    ("disciplinary.record_updated", "discipline", "/discipline"),
    ("administrative.account_updated", "announcements", "/account/security"),
]


@pytest_asyncio.fixture(autouse=True)
async def _clean_notification_tables(db_session: AsyncSession):
    yield
    for model in (
        FirebasePushSubscription,
        WebPushSubscription,
        NotificationDeviceProfile,
        NotificationOutboxEvent,
        UserNotification,
    ):
        await db_session.execute(delete(model))
    await db_session.execute(delete(NotificationDevice))
    await db_session.commit()


@pytest.mark.parametrize(
    "raw",
    [
        "https://evil.example/collect",
        "//evil.example/collect",
        "javascript:alert(1)",
        "",
        "   ",
        "/does-not-exist",
        "/finance-secret",
        "finance",
        "/../etc/passwd",
    ],
)
def test_unsafe_targets_fall_back_to_the_authenticated_inbox(raw: str) -> None:
    assert resolve_target_path(raw) == "/notifications"


@pytest.mark.parametrize(
    "raw",
    [
        "/dashboard",
        "/notifications",
        "/finance",
        "/finance?tab=custody",
        "/announcements",
        "/events",
        "/discipline",
        "/members/manage",
        "/documents",
        "/operation-journal",
        "/account/security",
        "/admin/notifications",
    ],
)
def test_representative_business_targets_are_preserved(raw: str) -> None:
    assert resolve_target_path(raw) == raw


@pytest.mark.asyncio
async def test_notify_normalizes_unsafe_target_and_writes_the_canonical_envelope(
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, "deep-envelope")
    service = UserNotificationService(db_session)

    created = await service.notify(
        tenant_id=context["tenant"].id,
        event_type="finance.payment_recorded",
        recipients=[context["user"].id],
        category="finance",
        target_path="https://evil.example/collect",
        deduplication_key="deep-envelope-1",
        metadata={"amount": "20.00"},
        priority="high",
        correlation_id="req-deep-1",
    )
    assert created is True
    await db_session.commit()

    event = await db_session.scalar(
        select(NotificationOutboxEvent).where(
            NotificationOutboxEvent.deduplication_key == "deep-envelope-1"
        )
    )
    assert event is not None
    payload = json.loads(event.payload_json)
    assert payload["envelope_version"] == 1
    assert payload["target_path"] == "/notifications"
    assert payload["category"] == "finance"
    assert payload["priority"] == "high"
    assert payload["correlation_id"] == "req-deep-1"
    assert payload["push_policy"] == "generic"


@pytest.mark.asyncio
async def test_representative_business_cases_reach_the_exact_target_with_generic_push(
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, "deep-cases")
    tenant_id = context["tenant"].id
    user_id = context["user"].id
    service = UserNotificationService(db_session)
    await service.save_subscription(
        tenant_id, user_id, INSTALLATION, "web", "test-agent", WEB_ENDPOINT, "p256dh", "auth"
    )
    await db_session.commit()

    web_push = FakeWebPushProvider()
    firebase_push = FakeFirebasePushProvider()
    processor = UserNotificationService(
        db_session, web_push_provider=web_push, firebase_push_provider=firebase_push
    )

    sensitive_markers = ("20.00", "Awa Ngono", "sanction")
    for index, (event_type, category, target) in enumerate(REPRESENTATIVE_CASES):
        await service.notify(
            tenant_id=tenant_id,
            event_type=event_type,
            recipients=[user_id],
            category=category,
            target_path=target,
            deduplication_key=f"deep-case-{index}",
            metadata={"amount": "20.00", "member": "Awa Ngono", "reason": "sanction"},
        )
        await db_session.commit()
        await processor.process_outbox()

        notification = await db_session.scalar(
            select(UserNotification).where(
                UserNotification.tenant_id == tenant_id,
                UserNotification.recipient_user_id == user_id,
                UserNotification.event_type == event_type,
            )
        )
        assert notification is not None
        assert notification.target_path == target

        _, message = web_push.sent[-1]
        assert message.target_path == target
        assert message.title == "Kairo"
        assert message.body == "Une nouvelle notification est disponible."
        for marker in sensitive_markers:
            assert marker not in message.body
            assert marker not in message.title
    assert len(web_push.sent) == len(REPRESENTATIVE_CASES)
    assert firebase_push.sent == []


@pytest.mark.asyncio
async def test_inbox_item_target_is_normalized_for_direct_enqueue(db_session: AsyncSession) -> None:
    context = await create_tenant_with_user(db_session, "deep-inbox")
    service = UserNotificationService(db_session)
    tenant_id = context["tenant"].id
    user_id = context["user"].id

    await service.enqueue(
        tenant_id=tenant_id,
        event_type="announcement.published",
        recipients=[user_id],
        category="announcements",
        target_path="https://evil.example/collect",
        deduplication_key="deep-inbox-1",
    )
    await db_session.commit()
    await UserNotificationService(db_session).process_outbox()

    notification = await db_session.scalar(
        select(UserNotification).where(UserNotification.tenant_id == tenant_id)
    )
    assert notification is not None
    assert notification.target_path == "/notifications"
