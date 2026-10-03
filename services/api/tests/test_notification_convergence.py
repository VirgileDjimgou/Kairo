"""Unified notification convergence coverage: envelope, transports, policy, health."""

from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from fakes import FakeFirebasePushProvider, FakeWebPushProvider
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from test_domain_events import _validated_receipt_context

from app.core.metrics import metrics
from app.modules.contributions.models import ContributionRecord
from app.modules.domain_events.models import DomainEvent
from app.modules.notifications.user_models import (
    FirebasePushSubscription,
    NotificationDevice,
    NotificationDeviceProfile,
    NotificationOutboxEvent,
    UserNotification,
    WebPushSubscription,
)
from app.modules.notifications.user_schemas import NotificationPreferencesUpdate
from app.modules.notifications.user_service import UserNotificationService
from app.providers.push.base import PushOutcome

WEB_ENDPOINT = "https://push.example.org/subscription/one"
INSTALLATION = "installation-convergence-0001"
ANDROID_INSTALLATION = "installation-android-0001"
FCM_TOKEN = "f" * 64


async def _drain_outbox(db_session: AsyncSession) -> None:
    """Drain events left by preceding scenarios; no providers are configured."""
    await UserNotificationService(db_session).process_outbox()


@pytest_asyncio.fixture(autouse=True)
async def _clean_notification_tables(db_session: AsyncSession):
    """Keep this file hermetic: the shared test connection keeps committed rows."""
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


async def _bind_push(
    db_session: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    *,
    installation_id: str = INSTALLATION,
    web: bool = True,
    firebase: bool = True,
    android_installation_id: str = ANDROID_INSTALLATION,
) -> None:
    service = UserNotificationService(db_session)
    await service.register_device(tenant_id, user_id, installation_id, "web", "test-agent")
    if web:
        await service.save_subscription(
            tenant_id,
            user_id,
            installation_id,
            "web",
            "test-agent",
            WEB_ENDPOINT,
            "p256dh-key-material",
            "auth-key-material",
        )
    if firebase:
        await service.save_firebase_subscription(
            tenant_id, user_id, android_installation_id, "test-agent", FCM_TOKEN
        )


@pytest.mark.asyncio
async def test_canonical_envelope_reaches_inbox_and_push(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await _validated_receipt_context(client, db_session)
    await _bind_push(db_session, context["tenant_id"], context["member_user_id"])
    web_push = FakeWebPushProvider()
    firebase_push = FakeFirebasePushProvider()

    service = UserNotificationService(
        db_session, web_push_provider=web_push, firebase_push_provider=firebase_push
    )
    await service.process_outbox()

    validated_event = await db_session.scalar(
        select(DomainEvent).where(
            DomainEvent.tenant_id == context["tenant_id"],
            DomainEvent.event_type == "finance.receipt_validated",
        )
    )
    assert validated_event is not None
    inbox_item = await db_session.scalar(
        select(UserNotification).where(
            UserNotification.tenant_id == context["tenant_id"],
            UserNotification.recipient_user_id == context["member_user_id"],
            UserNotification.event_type == "finance.receipt_validated",
        )
    )
    assert inbox_item is not None
    assert inbox_item.event_id == validated_event.id
    assert inbox_item.correlation_id is not None

    assert web_push.sent
    assert firebase_push.sent
    _, message = web_push.sent[0]
    assert message.body == "Une nouvelle notification est disponible."
    assert message.target_path == "/finance"
    assert "20.00" not in message.body


@pytest.mark.asyncio
async def test_push_preferences_filter_channels_but_not_the_inbox(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, f"conv-prefs-{uuid.uuid4().hex[:6]}")
    await _bind_push(db_session, context["tenant"].id, context["user"].id)
    service = UserNotificationService(db_session)
    await service.update_preferences(
        context["tenant"].id,
        context["user"].id,
        NotificationPreferencesUpdate(
            push_enabled=True,
            finance_enabled=True,
            discipline_enabled=True,
            announcements_enabled=False,
            events_enabled=True,
        ),
    )
    await _drain_outbox(db_session)
    web_push = FakeWebPushProvider()
    firebase_push = FakeFirebasePushProvider()
    service = UserNotificationService(
        db_session, web_push_provider=web_push, firebase_push_provider=firebase_push
    )
    assert await service.notify(
        tenant_id=context["tenant"].id,
        event_type="announcements.published",
        recipients=[context["user"].id],
        category="announcements",
        target_path="/announcements",
        deduplication_key="announcement-filter",
    )
    assert await service.notify(
        tenant_id=context["tenant"].id,
        event_type="finance.payment_recorded",
        recipients=[context["user"].id],
        category="finance",
        target_path="/finance",
        deduplication_key="finance-filter",
    )
    await db_session.commit()
    assert await service.process_outbox() == 2

    assert [message.target_path for _, message in web_push.sent] == ["/finance"]
    assert [message.target_path for _, message in firebase_push.sent] == ["/finance"]
    inbox_count = len(
        list(
            (
                await db_session.execute(
                    select(UserNotification).where(
                        UserNotification.tenant_id == context["tenant"].id,
                        UserNotification.recipient_user_id == context["user"].id,
                    )
                )
            ).scalars()
        )
    )
    assert inbox_count == 2


@pytest.mark.asyncio
async def test_invalid_push_targets_are_disabled(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, f"conv-invalid-{uuid.uuid4().hex[:6]}")
    await _bind_push(db_session, context["tenant"].id, context["user"].id)
    await _drain_outbox(db_session)
    web_push = FakeWebPushProvider([PushOutcome.INVALID_TARGET])
    firebase_push = FakeFirebasePushProvider([PushOutcome.INVALID_TARGET])
    service = UserNotificationService(
        db_session, web_push_provider=web_push, firebase_push_provider=firebase_push
    )
    await service.notify(
        tenant_id=context["tenant"].id,
        event_type="finance.payment_recorded",
        recipients=[context["user"].id],
        category="finance",
        target_path="/finance",
        deduplication_key="invalid-target",
    )
    await db_session.commit()
    assert await service.process_outbox() == 1

    web_subscription = await db_session.scalar(
        select(WebPushSubscription).where(
            WebPushSubscription.tenant_id == context["tenant"].id
        )
    )
    firebase_subscription = await db_session.scalar(
        select(FirebasePushSubscription).where(
            FirebasePushSubscription.tenant_id == context["tenant"].id
        )
    )
    assert web_subscription is not None and web_subscription.disabled_at is not None
    assert firebase_subscription is not None and firebase_subscription.disabled_at is not None
    assert metrics.push_deliveries[("web_push", "invalid_target")] == 1
    assert metrics.push_deliveries[("firebase", "invalid_target")] == 1


@pytest.mark.asyncio
async def test_transient_push_failure_uses_bounded_retry(
    client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.modules.notifications.outbox.service.PUSH_RETRY_BASE_SECONDS", 0.0
    )
    monkeypatch.setattr(
        "app.modules.notifications.outbox.service.PUSH_RETRY_MAX_SECONDS", 0.0
    )
    context = await create_tenant_with_user(db_session, f"conv-retry-{uuid.uuid4().hex[:6]}")
    await _bind_push(db_session, context["tenant"].id, context["user"].id, firebase=False)
    await _drain_outbox(db_session)
    web_push = FakeWebPushProvider([PushOutcome.TRANSIENT, PushOutcome.DELIVERED])
    firebase_push = FakeFirebasePushProvider()
    service = UserNotificationService(
        db_session, web_push_provider=web_push, firebase_push_provider=firebase_push
    )
    await service.notify(
        tenant_id=context["tenant"].id,
        event_type="finance.payment_recorded",
        recipients=[context["user"].id],
        category="finance",
        target_path="/finance",
        deduplication_key="transient-retry",
    )
    await db_session.commit()
    assert await service.process_outbox() == 1

    assert len(web_push.sent) == 2
    assert metrics.push_deliveries[("web_push", "delivered")] == 1
    web_subscription = await db_session.scalar(
        select(WebPushSubscription).where(
            WebPushSubscription.tenant_id == context["tenant"].id
        )
    )
    assert web_subscription is not None
    assert web_subscription.disabled_at is None
    assert web_subscription.failure_count == 0


@pytest.mark.asyncio
async def test_multiple_accounts_on_one_device_stay_isolated(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    first = await create_tenant_with_user(db_session, f"conv-shared-{uuid.uuid4().hex[:6]}")
    second = await create_user_for_tenant(
        db_session,
        tenant_id=first["tenant"].id,
        email=f"second-{uuid.uuid4().hex[:6]}@test.org",
        password="SecondPass123!",
        display_name="Second Account",
        role_code="member",
        profile_type="member",
    )
    await db_session.commit()
    await _bind_push(db_session, first["tenant"].id, first["user"].id, firebase=False)
    await _bind_push(db_session, first["tenant"].id, second["user"].id, web=False, firebase=False)
    await _drain_outbox(db_session)

    web_push = FakeWebPushProvider()
    service = UserNotificationService(
        db_session, web_push_provider=web_push, firebase_push_provider=FakeFirebasePushProvider()
    )
    await service.notify(
        tenant_id=first["tenant"].id,
        event_type="finance.payment_recorded",
        recipients=[first["user"].id],
        category="finance",
        target_path="/finance",
        deduplication_key="shared-device-first",
    )
    await db_session.commit()
    assert await service.process_outbox() == 1
    assert len(web_push.sent) == 1

    revoked = await service.revoke_device(
        first["tenant"].id, first["user"].id, INSTALLATION
    )
    assert revoked[0] == 1
    other_profile = await db_session.scalar(
        select(NotificationDeviceProfile).where(
            NotificationDeviceProfile.tenant_id == first["tenant"].id,
            NotificationDeviceProfile.user_id == second["user"].id,
        )
    )
    assert other_profile is not None
    assert other_profile.revoked_at is None
    assert other_profile.push_enabled is True


@pytest.mark.asyncio
async def test_revoke_device_endpoint_disables_only_current_profile(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, f"conv-revoke-{uuid.uuid4().hex[:6]}")
    await db_session.commit()
    token = await login(client, context["user"].email, context["password"], context["tenant"].slug)
    headers = {"Authorization": f"Bearer {token}"}
    registration = await client.post(
        "/api/v1/notifications/devices",
        json={"installation_id": INSTALLATION, "platform": "web"},
        headers=headers,
    )
    assert registration.status_code == 204, registration.text
    subscription = await client.post(
        "/api/v1/notifications/push-subscriptions",
        json={
            "installation_id": INSTALLATION,
            "platform": "web",
            "endpoint": WEB_ENDPOINT,
            "p256dh": "p256dh-key-material",
            "auth": "auth-key-material",
        },
        headers=headers,
    )
    assert subscription.status_code == 204, subscription.text

    revoked = await client.post(
        f"/api/v1/notifications/devices/{INSTALLATION}/revoke", headers=headers
    )
    assert revoked.status_code == 200, revoked.text
    body = revoked.json()
    assert body["revoked_profiles"] == 1
    assert body["disabled_web_subscriptions"] == 1

    profile = await db_session.scalar(
        select(NotificationDeviceProfile).where(
            NotificationDeviceProfile.tenant_id == context["tenant"].id
        )
    )
    web_subscription = await db_session.scalar(
        select(WebPushSubscription).where(
            WebPushSubscription.tenant_id == context["tenant"].id
        )
    )
    assert profile is not None and profile.revoked_at is not None
    assert web_subscription is not None and web_subscription.disabled_at is not None

    re_registered = await client.post(
        "/api/v1/notifications/push-subscriptions",
        json={
            "installation_id": INSTALLATION,
            "platform": "web",
            "endpoint": WEB_ENDPOINT,
            "p256dh": "p256dh-key-material",
            "auth": "auth-key-material",
        },
        headers=headers,
    )
    assert re_registered.status_code == 204, re_registered.text
    await db_session.refresh(profile)
    await db_session.refresh(web_subscription)
    assert profile.revoked_at is None
    assert web_subscription.disabled_at is None


@pytest.mark.asyncio
async def test_notification_health_endpoint_is_admin_only_and_secret_free(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"conv-health-{uuid.uuid4().hex[:6]}")
    member = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"health-member-{uuid.uuid4().hex[:6]}@test.org",
        password="MemberPass123!",
        display_name="Health Member",
        role_code="member",
        profile_type="member",
    )
    await db_session.commit()
    admin_token = await login(client, admin["user"].email, admin["password"], admin["tenant"].slug)
    member_token = await login(
        client, member["user"].email, member["password"], admin["tenant"].slug
    )

    forbidden = await client.get(
        "/api/v1/notifications/health",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert forbidden.status_code == 403

    response = await client.get(
        "/api/v1/notifications/health",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert set(body) == {
        "web_push_configured",
        "firebase_configured",
        "worker_running",
        "pending_outbox",
        "failed_outbox",
        "oldest_pending_seconds",
        "disabled_web_subscriptions",
        "disabled_fcm_tokens",
        "retrying_web_subscriptions",
        "retrying_fcm_tokens",
        "stranded_outbox",
        "retrying_outbox",
        "last_successful_dispatch_at",
    }
    raw = response.text.lower()
    assert '"fcm_token":' not in raw
    assert "private_key" not in raw
    assert "service_account" not in raw


@pytest.mark.asyncio
async def test_notification_metrics_surface_outbox_and_disabled_counts(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, f"conv-metrics-{uuid.uuid4().hex[:6]}")
    await db_session.commit()
    token = await login(client, context["user"].email, context["password"], context["tenant"].slug)
    await _drain_outbox(db_session)
    service = UserNotificationService(db_session)
    await service.notify(
        tenant_id=context["tenant"].id,
        event_type="finance.payment_recorded",
        recipients=[context["user"].id],
        category="finance",
        target_path="/finance",
        deduplication_key="metrics-pending",
    )
    await db_session.commit()

    metrics_response = await client.get("/metrics", headers={"Authorization": f"Bearer {token}"})
    assert metrics_response.status_code == 200
    text = metrics_response.text
    for name in (
        "kairo_notification_outbox_pending",
        "kairo_notification_outbox_failed",
        "kairo_notification_outbox_oldest_age_seconds",
        "kairo_disabled_web_subscriptions",
        "kairo_disabled_fcm_tokens",
        "kairo_push_deliveries_total",
        "kairo_web_push_success_total",
        "kairo_web_push_failure_total",
        "kairo_fcm_success_total",
        "kairo_fcm_failure_total",
    ):
        assert name in text
    assert "kairo_notification_outbox_pending 1" in text


@pytest.mark.asyncio
async def test_admin_module_has_data_supports_notifications_module(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, f"conv-module-{uuid.uuid4().hex[:6]}")
    await db_session.commit()
    token = await login(client, context["user"].email, context["password"], context["tenant"].slug)
    headers = {"Authorization": f"Bearer {token}"}

    empty = await client.get("/api/v1/admin/module-has-data", params={"module": "notifications"}, headers=headers)
    assert empty.status_code == 200, empty.text
    assert empty.json() == {"module": "notifications", "has_data": False}

    await _drain_outbox(db_session)
    service = UserNotificationService(
        db_session,
        web_push_provider=FakeWebPushProvider(),
        firebase_push_provider=FakeFirebasePushProvider(),
    )
    await service.notify(
        tenant_id=context["tenant"].id,
        event_type="finance.payment_recorded",
        recipients=[context["user"].id],
        category="finance",
        target_path="/finance",
        deduplication_key="module-data",
    )
    await db_session.commit()
    assert await service.process_outbox() == 1

    populated = await client.get("/api/v1/admin/module-has-data", params={"module": "notifications"}, headers=headers)
    assert populated.status_code == 200, populated.text
    assert populated.json() == {"module": "notifications", "has_data": True}


@pytest.mark.asyncio
async def test_producers_route_through_the_canonical_pipeline(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"conv-producers-{uuid.uuid4().hex[:6]}")
    treasurer = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"producer-treasurer-{uuid.uuid4().hex[:6]}@test.org",
        password="TreasurerPass123!",
        display_name="Producer Treasurer",
        role_code="treasurer",
        profile_type="staff",
    )
    auditor = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"producer-auditor-{uuid.uuid4().hex[:6]}@test.org",
        password="AuditorPass123!",
        display_name="Producer Auditor",
        role_code="auditor",
        profile_type="staff",
    )
    member = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"producer-member-{uuid.uuid4().hex[:6]}@test.org",
        password="MemberPass123!",
        display_name="Producer Member",
        role_code="member",
        profile_type="member",
        member_code=f"PRD-{uuid.uuid4().hex[:6]}",
    )
    await db_session.commit()
    admin_token = await login(client, admin["user"].email, admin["password"], admin["tenant"].slug)
    treasurer_token = await login(
        client, treasurer["user"].email, treasurer["password"], admin["tenant"].slug
    )

    announcement = await client.post(
        "/api/v1/announcements/",
        json={
            "title": "Convergence announcement",
            "body": "Pipeline coverage",
            "visibility_scope": "tenant_public",
            "status": "published",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert announcement.status_code == 201, announcement.text

    event = await client.post(
        "/api/v1/events/",
        json={
            "title": "Convergence event",
            "description": "Pipeline coverage",
            "start_at": "2026-10-01T18:00:00Z",
            "end_at": "2026-10-01T20:00:00Z",
            "location": "Hall",
            "status": "published",
            "visibility_scope": "tenant_public",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert event.status_code == 201, event.text

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
    payment = await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": contribution.json()["id"],
            "amount": "20.00",
            "currency": "EUR",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert payment.status_code == 201, payment.text

    expense = await client.post(
        "/api/v1/contributions/expenses",
        json={
            "category": "administration",
            "amount": "5.00",
            "currency": "EUR",
            "description": "Office supplies",
        },
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )
    assert expense.status_code == 201, expense.text

    rows = list(
        (
            await db_session.execute(
                select(NotificationOutboxEvent).where(
                    NotificationOutboxEvent.tenant_id == admin["tenant"].id
                )
            )
        ).scalars()
    )
    by_key = {row.deduplication_key: row for row in rows}
    assert f"announcement-published:{announcement.json()['id']}" in by_key
    assert f"event-published:{event.json()['id']}" in by_key
    assert f"payment-recorded:{payment.json()['id']}" in by_key
    assert f"expense-recorded:{expense.json()['id']}" in by_key

    payment_row = by_key[f"payment-recorded:{payment.json()['id']}"]
    assert member["user"].id in _recipients(payment_row)
    expense_row = by_key[f"expense-recorded:{expense.json()['id']}"]
    assert _recipients(expense_row) == [auditor["user"].id]


class _RaisingWebPushProvider:
    """Transport double whose provider boundary raises instead of returning."""

    def __init__(self) -> None:
        self.calls = 0

    def send(self, target: object, message: object) -> PushOutcome:
        self.calls += 1
        raise RuntimeError("push transport crashed")


@pytest.mark.asyncio
async def test_push_provider_outage_keeps_the_inbox_and_contains_the_failure(
    client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.modules.notifications.outbox.service.PUSH_RETRY_BASE_SECONDS", 0.0
    )
    monkeypatch.setattr(
        "app.modules.notifications.outbox.service.PUSH_RETRY_MAX_SECONDS", 0.0
    )
    context = await create_tenant_with_user(db_session, f"conv-outage-{uuid.uuid4().hex[:6]}")
    await _bind_push(db_session, context["tenant"].id, context["user"].id, firebase=False)
    await _drain_outbox(db_session)
    web_push = FakeWebPushProvider([PushOutcome.TRANSIENT] * 9)
    service = UserNotificationService(
        db_session, web_push_provider=web_push, firebase_push_provider=FakeFirebasePushProvider()
    )
    await service.notify(
        tenant_id=context["tenant"].id,
        event_type="finance.payment_recorded",
        recipients=[context["user"].id],
        category="finance",
        target_path="/finance",
        deduplication_key="provider-outage",
    )
    await db_session.commit()

    assert await service.process_outbox() == 1

    event = await db_session.scalar(
        select(NotificationOutboxEvent).where(
            NotificationOutboxEvent.tenant_id == context["tenant"].id
        )
    )
    assert event is not None
    assert event.status == "completed"
    assert len(web_push.sent) == 3
    inbox_items = list(
        (
            await db_session.execute(
                select(UserNotification).where(UserNotification.tenant_id == context["tenant"].id)
            )
        ).scalars()
    )
    assert len(inbox_items) == 1
    subscription = await db_session.scalar(
        select(WebPushSubscription).where(WebPushSubscription.tenant_id == context["tenant"].id)
    )
    assert subscription is not None
    assert subscription.disabled_at is None
    assert subscription.failure_count == 1
    assert metrics.push_deliveries[("web_push", "transient")] >= 1

    assert await service.process_outbox() == 0
    repeated = await db_session.scalar(
        select(func.count(UserNotification.id)).where(
            UserNotification.tenant_id == context["tenant"].id
        )
    )
    assert repeated == 1


@pytest.mark.asyncio
async def test_unexpected_provider_exception_is_contained_as_a_transient_failure(
    client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.modules.notifications.outbox.service.PUSH_RETRY_BASE_SECONDS", 0.0
    )
    monkeypatch.setattr(
        "app.modules.notifications.outbox.service.PUSH_RETRY_MAX_SECONDS", 0.0
    )
    context = await create_tenant_with_user(db_session, f"conv-raised-{uuid.uuid4().hex[:6]}")
    await _bind_push(db_session, context["tenant"].id, context["user"].id, firebase=False)
    await _drain_outbox(db_session)
    raising = _RaisingWebPushProvider()
    service = UserNotificationService(
        db_session,
        web_push_provider=raising,  # type: ignore[arg-type]
        firebase_push_provider=FakeFirebasePushProvider(),
    )
    await service.notify(
        tenant_id=context["tenant"].id,
        event_type="finance.payment_recorded",
        recipients=[context["user"].id],
        category="finance",
        target_path="/finance",
        deduplication_key="provider-raised",
    )
    await db_session.commit()

    assert await service.process_outbox() == 1

    assert raising.calls == 3
    event = await db_session.scalar(
        select(NotificationOutboxEvent).where(
            NotificationOutboxEvent.tenant_id == context["tenant"].id
        )
    )
    assert event is not None
    assert event.status == "completed"
    assert event.last_error is None
    inbox_count = await db_session.scalar(
        select(func.count(UserNotification.id)).where(
            UserNotification.tenant_id == context["tenant"].id
        )
    )
    assert inbox_count == 1


@pytest.mark.asyncio
async def test_worker_outage_defers_delivery_but_preserves_business_state(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await _validated_receipt_context(client, db_session)
    contribution = await db_session.get(
        ContributionRecord, uuid.UUID(context["contribution_id"])
    )
    assert contribution is not None
    paid_before = contribution.paid_amount

    inbox_before = await db_session.scalar(
        select(func.count(UserNotification.id)).where(
            UserNotification.tenant_id == context["tenant_id"]
        )
    )
    assert inbox_before == 0

    await _drain_outbox(db_session)

    inbox_items = list(
        (
            await db_session.execute(
                select(UserNotification).where(UserNotification.tenant_id == context["tenant_id"])
            )
        ).scalars()
    )
    assert inbox_items
    assert any(item.recipient_user_id == context["member_user_id"] for item in inbox_items)
    assert all(item.deduplication_key for item in inbox_items)

    await db_session.refresh(contribution)
    assert contribution.paid_amount == paid_before

    assert await UserNotificationService(db_session).process_outbox() == 0
    inbox_after = await db_session.scalar(
        select(func.count(UserNotification.id)).where(
            UserNotification.tenant_id == context["tenant_id"]
        )
    )
    assert inbox_after == len(inbox_items)


def _recipients(row: NotificationOutboxEvent) -> list[uuid.UUID]:
    import json

    return [uuid.UUID(raw) for raw in json.loads(row.payload_json)["recipients"]]
