"""Outbox reliability: leases, reclaim, idempotency, dead-letter and telemetry."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from fakes import FakeWebPushProvider
from helpers import create_tenant_with_user
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.domain_events.models import (
    EVENT_STATUS_COMPLETED,
    EVENT_STATUS_PENDING,
    EVENT_STATUS_PROCESSING,
    DomainEvent,
)
from app.modules.domain_events.service import DomainEventService
from app.modules.notifications.user_models import (
    FirebasePushSubscription,
    NotificationDevice,
    NotificationDeviceProfile,
    NotificationOutboxEvent,
    UserNotification,
    WebPushSubscription,
)
from app.modules.notifications.user_service import UserNotificationService

INSTALLATION = "installation-reliability-0001"
WEB_ENDPOINT = "https://push.example.org/reliability/web"


def _stale_moment() -> datetime:
    return datetime.now(UTC) - timedelta(
        seconds=settings.outbox_processing_lease_seconds + 60
    )


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
    await db_session.execute(delete(DomainEvent))
    await db_session.execute(delete(NotificationDevice))
    await db_session.commit()


async def _seed_notification_event(
    db_session: AsyncSession, suffix: str
) -> tuple[dict, NotificationOutboxEvent]:
    context = await create_tenant_with_user(db_session, f"reliability-{suffix}")
    service = UserNotificationService(db_session)
    await service.save_subscription(
        context["tenant"].id,
        context["user"].id,
        INSTALLATION,
        "web",
        "test-agent",
        WEB_ENDPOINT,
        "p256dh",
        "auth",
    )
    await service.enqueue(
        tenant_id=context["tenant"].id,
        event_type="announcement.published",
        recipients=[context["user"].id],
        category="announcements",
        target_path="/announcements",
        deduplication_key=f"reliability-{suffix}",
    )
    await db_session.commit()
    event = await db_session.scalar(
        select(NotificationOutboxEvent).where(
            NotificationOutboxEvent.deduplication_key == f"reliability-{suffix}"
        )
    )
    assert event is not None
    return context, event


@pytest.mark.asyncio
async def test_expired_processing_lease_is_reclaimed_and_delivered(
    db_session: AsyncSession,
) -> None:
    context, event = await _seed_notification_event(db_session, "expired")
    event.status, event.attempts, event.processing_started_at = (
        "processing",
        1,
        _stale_moment(),
    )
    await db_session.commit()

    web_push = FakeWebPushProvider()
    service = UserNotificationService(db_session, web_push_provider=web_push)
    completed = await service.process_outbox()

    assert completed == 1
    await db_session.refresh(event)
    assert event.status == "completed"
    assert event.processing_started_at is None
    assert len(web_push.sent) == 1
    inbox_count = int(
        await db_session.scalar(
            select(func.count(UserNotification.id)).where(
                UserNotification.tenant_id == context["tenant"].id
            )
        )
        or 0
    )
    assert inbox_count == 1


@pytest.mark.asyncio
async def test_fresh_processing_lease_is_not_reclaimed(db_session: AsyncSession) -> None:
    _context, event = await _seed_notification_event(db_session, "fresh")
    event.status, event.attempts, event.processing_started_at = (
        "processing",
        1,
        datetime.now(UTC),
    )
    await db_session.commit()

    web_push = FakeWebPushProvider()
    service = UserNotificationService(db_session, web_push_provider=web_push)
    assert await service.process_outbox() == 0
    await db_session.refresh(event)
    assert event.status == "processing"
    assert web_push.sent == []

    report = await service.reconcile_outbox()
    assert report["stranded"] == 0
    assert report["pending"] == 0


@pytest.mark.asyncio
async def test_reclaimed_event_does_not_duplicate_inbox_rows(
    db_session: AsyncSession,
) -> None:
    context, event = await _seed_notification_event(db_session, "idempotent")
    # Simulate a crash after the inbox projection committed but before the
    # outbox event was marked completed.
    db_session.add(
        UserNotification(
            tenant_id=context["tenant"].id,
            recipient_user_id=context["user"].id,
            event_type="announcement.published",
            category="announcements",
            priority="normal",
            target_path="/announcements",
            metadata_json="{}",
            deduplication_key=f"{event.deduplication_key}:{context['user'].id}",
        )
    )
    event.status, event.attempts, event.processing_started_at = (
        "processing",
        1,
        _stale_moment(),
    )
    await db_session.commit()

    web_push = FakeWebPushProvider()
    service = UserNotificationService(db_session, web_push_provider=web_push)
    assert await service.process_outbox() == 1
    await db_session.refresh(event)
    assert event.status == "completed"

    inbox_count = int(
        await db_session.scalar(
            select(func.count(UserNotification.id)).where(
                UserNotification.tenant_id == context["tenant"].id
            )
        )
        or 0
    )
    assert inbox_count == 1


@pytest.mark.asyncio
async def test_terminal_failure_becomes_dead_letter(
    db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    context, event = await _seed_notification_event(db_session, "dead-letter")

    async def _explode(self, _event, _push_title):  # noqa: ANN001
        raise RuntimeError("delivery exploded")

    monkeypatch.setattr(UserNotificationService, "_deliver_event", _explode)
    event.status = "pending"
    event.attempts = 4
    event.available_at = datetime.now(UTC) - timedelta(seconds=1)
    await db_session.commit()

    service = UserNotificationService(db_session)
    assert await service.process_outbox() == 0
    await db_session.refresh(event)
    assert event.status == "failed"
    assert event.last_error == "RuntimeError"
    assert event.processing_started_at is None

    report = await service.reconcile_outbox()
    assert report["dead_letter"] == 1

    health = await service.health(context["tenant"].id)
    assert health.failed_outbox == 1


@pytest.mark.asyncio
async def test_health_and_reconciliation_expose_stranded_and_retrying(
    db_session: AsyncSession,
) -> None:
    context, event = await _seed_notification_event(db_session, "telemetry")
    event.status, event.attempts, event.processing_started_at = (
        "processing",
        1,
        _stale_moment(),
    )
    db_session.add(
        NotificationOutboxEvent(
            tenant_id=context["tenant"].id,
            event_type="announcement.published",
            payload_json="{}",
            deduplication_key="reliability-telemetry-retrying",
            status="pending",
            attempts=2,
            available_at=datetime.now(UTC) + timedelta(minutes=5),
        )
    )
    await db_session.commit()

    service = UserNotificationService(db_session)
    health = await service.health(context["tenant"].id)
    assert health.stranded_outbox == 1
    assert health.retrying_outbox == 1

    report = await service.reconcile_outbox()
    assert report["reclaimed"] == 1
    assert report["retrying"] == 2
    assert report["stranded"] == 0
    await db_session.refresh(event)
    assert event.status == "pending"
    assert event.last_error == "stale_processing_reclaimed"


@pytest.mark.asyncio
async def test_domain_event_processing_lease_is_reclaimed(
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, "reliability-domain")
    service = DomainEventService(db_session)
    event = await service.publish(
        tenant_id=context["tenant"].id,
        event_type="reliability.no_handlers",
        aggregate_type="reliability",
        aggregate_id=uuid.uuid4(),
        deduplication_key="reliability-domain-1",
        dispatch=False,
    )
    await db_session.commit()
    event.status = EVENT_STATUS_PROCESSING
    event.processing_started_at = _stale_moment()
    await db_session.commit()

    reclaimed = await service.reclaim_stale_events()
    assert reclaimed == 1
    await db_session.refresh(event)
    assert event.status == EVENT_STATUS_PENDING

    completed = await service.process_pending()
    assert completed == 1
    await db_session.refresh(event)
    assert event.status == EVENT_STATUS_COMPLETED
    assert event.processing_started_at is None
