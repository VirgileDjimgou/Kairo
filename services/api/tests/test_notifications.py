"""Sprint 14 integration tests: multi-channel notification placeholders."""

from __future__ import annotations

import uuid as _uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from helpers import create_tenant_with_user, login
from helpers import create_user_for_tenant
from fakes import (
    FakeEmailNotificationProvider,
    FakeTelegramNotificationProvider,
    FakeWhatsAppNotificationProvider,
)
from test_events_announcements import _create_linked_member


class _FakeSimulationProvider:
    def __init__(self, channel: str, display_name: str) -> None:
        self.channel = channel
        self._display_name = display_name

    def describe(self):
        from app.providers.notifications.base import NotificationChannelDescriptor

        return NotificationChannelDescriptor(
            channel=self.channel,
            display_name=self._display_name,
            description=f"{self._display_name} placeholder.",
            configured=False,
            simulation_only=True,
            target_hint="Target",
        )

    async def send_message(self, **kwargs):
        from app.providers.notifications.base import NotificationDispatchResult

        return NotificationDispatchResult(
            channel=self.channel,
            status="simulated",
            message="Simulation only.",
            delivered=False,
            simulation_only=True,
        )

    async def send_test_message(self, **kwargs):
        return await self.send_message(**kwargs)

    async def fetch_delivery_status(self, **kwargs):
        return None


@pytest.mark.asyncio
async def test_telegram_provider_reports_live_when_token_is_configured(monkeypatch) -> None:
    from app.core.config import settings
    from app.providers.notifications.placeholders import TelegramNotificationProvider

    monkeypatch.setattr(settings, "telegram_bot_token", "telegram-token")
    provider = TelegramNotificationProvider()

    descriptor = provider.describe()
    assert descriptor.channel == "telegram"
    assert descriptor.configured is True
    assert descriptor.simulation_only is False
    assert "Telegram Bot API" in descriptor.description


@pytest.mark.asyncio
async def test_telegram_provider_send_message_returns_sent_when_api_call_succeeds(monkeypatch) -> None:
    from app.core.config import settings
    from app.providers.notifications.placeholders import TelegramNotificationProvider

    monkeypatch.setattr(settings, "telegram_bot_token", "telegram-token")
    provider = TelegramNotificationProvider()
    captured: dict[str, str | None] = {}

    async def fake_send(*, recipient: str, subject: str | None, body: str) -> None:
        captured["recipient"] = recipient
        captured["subject"] = subject
        captured["body"] = body

    monkeypatch.setattr(provider, "_send_via_telegram", fake_send)
    result = await provider.send_message(
        tenant_id=_uuid.uuid4(),
        actor_user_id=_uuid.uuid4(),
        recipient="@ops_room",
        subject="Ops alert",
        body="Background worker needs attention.",
    )

    assert result.channel == "telegram"
    assert result.status == "sent"
    assert result.delivered is True
    assert result.simulation_only is False
    assert captured["recipient"] == "@ops_room"
    assert captured["subject"] == "Ops alert"
    assert captured["body"] == "Background worker needs attention."


@pytest.mark.asyncio
async def test_whatsapp_provider_reports_live_when_gateway_is_configured(monkeypatch) -> None:
    from app.core.config import settings
    from app.providers.notifications.placeholders import WhatsAppNotificationProvider

    monkeypatch.setattr(settings, "whatsapp_api_base_url", "https://wa-gateway.example")
    monkeypatch.setattr(settings, "whatsapp_api_token", "wa-token")
    provider = WhatsAppNotificationProvider()

    descriptor = provider.describe()
    assert descriptor.channel == "whatsapp"
    assert descriptor.configured is True
    assert descriptor.simulation_only is False
    assert "Gateway-backed provider" in descriptor.description


@pytest.mark.asyncio
async def test_whatsapp_provider_send_message_returns_sent_when_gateway_call_succeeds(monkeypatch) -> None:
    from app.core.config import settings
    from app.providers.notifications.placeholders import WhatsAppNotificationProvider

    monkeypatch.setattr(settings, "whatsapp_api_base_url", "https://wa-gateway.example")
    monkeypatch.setattr(settings, "whatsapp_api_token", "wa-token")
    provider = WhatsAppNotificationProvider()
    captured: dict[str, str | None] = {}

    async def fake_send(*, recipient: str, subject: str | None, body: str) -> None:
        captured["recipient"] = recipient
        captured["subject"] = subject
        captured["body"] = body

    monkeypatch.setattr(provider, "_send_via_gateway", fake_send)
    result = await provider.send_message(
        tenant_id=_uuid.uuid4(),
        actor_user_id=_uuid.uuid4(),
        recipient="+49123456789",
        subject="WhatsApp alert",
        body="A payment workflow needs attention.",
    )

    assert result.channel == "whatsapp"
    assert result.status == "sent"
    assert result.delivered is True
    assert result.simulation_only is False
    assert captured["recipient"] == "+49123456789"
    assert captured["subject"] == "WhatsApp alert"
    assert captured["body"] == "A payment workflow needs attention."


@pytest.mark.asyncio
async def test_admin_can_list_notification_channels(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"notif-list-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)

    response = await client.get(
        "/api/v1/notifications/channels",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    channels = response.json()
    assert [channel["channel"] for channel in channels] == ["email", "telegram", "whatsapp"]
    assert all(channel["simulation_only"] is True for channel in channels)


@pytest.mark.asyncio
async def test_non_admin_cannot_list_notification_channels(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"notif-lock-{_uuid.uuid4().hex[:6]}")
    member = await _create_linked_member(
        db_session,
        tenant_id=ctx["tenant"].id,
        email=f"member-notif-{_uuid.uuid4().hex[:6]}@test.org",
        password="NotifMember1!",
        member_code="NT-001",
        display_name="Notification Member",
    )
    token = await login(client, member["user"].email, member["password"], tenant_slug=ctx["tenant"].slug)

    response = await client.get(
        "/api/v1/notifications/channels",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_send_simulated_multi_channel_notification(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"notif-send-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)

    response = await client.post(
        "/api/v1/notifications/test",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "channels": ["email", "telegram", "email"],
            "recipient": "ops@example.org",
            "subject": "Kairo test",
            "body": "This is a dry-run notification.",
        },
    )
    assert response.status_code == 200, response.text
    results = response.json()["results"]
    assert [item["channel"] for item in results] == ["email", "telegram"]
    assert all(item["status"] == "simulated" for item in results)
    assert all(item["delivered"] is False for item in results)
    assert all(item["simulation_only"] is True for item in results)


@pytest.mark.asyncio
async def test_principal_admin_can_list_and_send_notification_channels(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"notif-principal-{_uuid.uuid4().hex[:6]}")
    principal = await create_user_for_tenant(
        db_session,
        tenant_id=ctx["tenant"].id,
        email=f"principal-notif-{_uuid.uuid4().hex[:6]}@test.org",
        password="PrincipalPass1!",
        display_name="Principal Admin",
        role_code="principal_admin",
        profile_type="admin",
    )
    await db_session.commit()

    token = await login(client, principal["user"].email, principal["password"], tenant_slug=ctx["tenant"].slug)

    response = await client.get(
        "/api/v1/notifications/channels",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    channels = response.json()
    assert [channel["channel"] for channel in channels] == ["email", "telegram", "whatsapp"]

    sent = await client.post(
        "/api/v1/notifications/test",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "channels": ["email"],
            "recipient": "ops@example.org",
            "subject": "Principal admin check",
            "body": "Tenant control plane dry-run.",
        },
    )
    assert sent.status_code == 200, sent.text


@pytest.mark.asyncio
async def test_unknown_notification_channel_is_rejected(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"notif-err-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)

    response = await client.post(
        "/api/v1/notifications/test",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "channels": ["pagerduty"],
            "recipient": "ops@example.org",
            "body": "Unsupported channel test",
        },
    )
    assert response.status_code == 400
    assert "Unknown notification channel" in response.json()["detail"]


@pytest.mark.asyncio
async def test_admin_can_send_live_email_notification_when_email_provider_is_live_capable(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    from app.core.dependencies import get_notification_providers
    from app.main import app

    ctx = await create_tenant_with_user(db_session, f"notif-live-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)
    provider = FakeEmailNotificationProvider(
        configured=True,
        status="sent",
        delivered=True,
        simulation_only=False,
        message="SMTP accepted the operator notification.",
    )
    app.dependency_overrides[get_notification_providers] = lambda: [
        provider,
        _FakeSimulationProvider("telegram", "Telegram"),
        _FakeSimulationProvider("whatsapp", "WhatsApp"),
    ]

    try:
        response = await client.post(
            "/api/v1/notifications/dispatch",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "email",
                "recipient": "ops@example.org",
                "subject": "Kairo live notification",
                "body": "This email validates the live operator notification path.",
            },
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["channel"] == "email"
    assert body["status"] == "sent"
    assert body["delivered"] is True
    assert body["simulation_only"] is False
    assert body["delivery_stage"] == "accepted"
    assert body["reconciliation_status"] == "pending"
    assert body["reconciliation_supported"] is True
    assert body["provider_reference"] == "fake-email-ref"
    assert provider.calls[0]["tenant_id"] == str(ctx["tenant"].id)
    assert provider.calls[0]["recipient"] == "ops@example.org"


@pytest.mark.asyncio
async def test_admin_can_review_notification_history_with_reconciliation_metadata(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    from app.core.dependencies import get_notification_providers
    from app.main import app

    ctx = await create_tenant_with_user(db_session, f"notif-history-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)
    app.dependency_overrides[get_notification_providers] = lambda: [
        FakeEmailNotificationProvider(
            configured=True,
            status="sent",
            delivered=True,
            simulation_only=False,
            message="SMTP accepted the operator notification.",
            provider_reference="smtp-history-ref",
        ),
        _FakeSimulationProvider("telegram", "Telegram"),
    ]

    try:
        live = await client.post(
            "/api/v1/notifications/dispatch",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "email",
                "recipient": "ops@example.org",
                "subject": "History check",
                "body": "Live delivery evidence.",
            },
        )
        simulated = await client.post(
            "/api/v1/notifications/test",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channels": ["telegram"],
                "recipient": "@ops-room",
                "subject": "History simulation",
                "body": "Dry-run evidence.",
            },
        )
        history = await client.get(
            "/api/v1/notifications/history",
            headers={"Authorization": f"Bearer {token}"},
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert live.status_code == 200, live.text
    assert simulated.status_code == 200, simulated.text
    assert history.status_code == 200, history.text
    rows = history.json()
    assert len(rows) == 2
    by_action = {row["action"]: row for row in rows}
    assert by_action["notification_test"]["channel"] == "telegram"
    assert by_action["notification_test"]["delivery_stage"] == "simulated"
    assert by_action["notification_test"]["reconciliation_status"] == "not_applicable"
    assert by_action["notification_test"]["provider_reference"] is None
    assert by_action["notification_dispatch"]["channel"] == "email"
    assert by_action["notification_dispatch"]["delivery_stage"] == "accepted"
    assert by_action["notification_dispatch"]["reconciliation_status"] == "pending"
    assert by_action["notification_dispatch"]["reconciliation_supported"] is True
    assert by_action["notification_dispatch"]["provider_reference"] == "smtp-history-ref"


@pytest.mark.asyncio
async def test_provider_callback_can_mark_live_notification_as_delivered(
    client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch,
) -> None:
    from app.core.config import settings
    from app.core.dependencies import get_notification_providers
    from app.main import app

    monkeypatch.setattr(settings, "notification_reconciliation_callback_token", "callback-secret")
    ctx = await create_tenant_with_user(db_session, f"notif-callback-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)
    app.dependency_overrides[get_notification_providers] = lambda: [
        FakeWhatsAppNotificationProvider(
            configured=True,
            status="sent",
            delivered=True,
            simulation_only=False,
            message="WhatsApp accepted the operator notification.",
            provider_reference="wa-live-ref",
        )
    ]

    try:
        dispatch = await client.post(
            "/api/v1/notifications/dispatch",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "whatsapp",
                "recipient": "+49123456789",
                "subject": "Callback check",
                "body": "Waiting for provider delivery confirmation.",
            },
        )
        callback = await client.post(
            "/api/v1/notifications/reconciliation/callback",
            headers={"X-Kairo-Notification-Token": "callback-secret"},
            json={
                "tenant_id": str(ctx["tenant"].id),
                "channel": "whatsapp",
                "provider_reference": "wa-live-ref",
                "delivery_stage": "delivered",
                "provider_message": "Gateway confirmed final delivery.",
                "external_status": "delivered",
            },
        )
        history = await client.get(
            "/api/v1/notifications/history",
            headers={"Authorization": f"Bearer {token}"},
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert dispatch.status_code == 200, dispatch.text
    assert callback.status_code == 200, callback.text
    assert history.status_code == 200, history.text
    row = history.json()[0]
    assert row["channel"] == "whatsapp"
    assert row["delivery_stage"] == "delivered"
    assert row["reconciliation_status"] == "delivered"
    assert row["delivered"] is True
    assert row["provider_reference"] == "wa-live-ref"
    assert row["message"] == "Gateway confirmed final delivery."
    assert row["polling_supported"] is True


@pytest.mark.asyncio
async def test_provider_callback_is_replay_safe_for_identical_final_state(
    client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch,
) -> None:
    from app.core.config import settings
    from app.core.dependencies import get_notification_providers
    from app.main import app

    monkeypatch.setattr(settings, "notification_reconciliation_callback_token", "callback-secret")
    ctx = await create_tenant_with_user(db_session, f"notif-callback-replay-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)
    app.dependency_overrides[get_notification_providers] = lambda: [
        FakeWhatsAppNotificationProvider(
            configured=True,
            status="sent",
            delivered=True,
            simulation_only=False,
            provider_reference="wa-replay-ref",
        )
    ]

    try:
        dispatch = await client.post(
            "/api/v1/notifications/dispatch",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "whatsapp",
                "recipient": "+49123456789",
                "subject": "Replay check",
                "body": "Waiting for provider delivery confirmation.",
            },
        )
        first_callback = await client.post(
            "/api/v1/notifications/reconciliation/callback",
            headers={"X-Kairo-Notification-Token": "callback-secret"},
            json={
                "tenant_id": str(ctx["tenant"].id),
                "channel": "whatsapp",
                "provider_reference": "wa-replay-ref",
                "delivery_stage": "delivered",
                "provider_message": "Gateway confirmed final delivery.",
                "external_status": "delivered",
            },
        )
        second_callback = await client.post(
            "/api/v1/notifications/reconciliation/callback",
            headers={"X-Kairo-Notification-Token": "callback-secret"},
            json={
                "tenant_id": str(ctx["tenant"].id),
                "channel": "whatsapp",
                "provider_reference": "wa-replay-ref",
                "delivery_stage": "delivered",
                "provider_message": "Gateway confirmed final delivery.",
                "external_status": "delivered",
            },
        )
        history = await client.get(
            "/api/v1/notifications/history",
            headers={"Authorization": f"Bearer {token}"},
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert dispatch.status_code == 200, dispatch.text
    assert first_callback.status_code == 200, first_callback.text
    assert second_callback.status_code == 200, second_callback.text
    assert second_callback.json()["updated"] is False
    assert history.status_code == 200, history.text
    rows = history.json()
    assert len(rows) == 1
    assert rows[0]["delivery_stage"] == "delivered"


@pytest.mark.asyncio
async def test_admin_can_poll_pending_whatsapp_notification_to_final_state(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    from app.core.dependencies import get_notification_providers
    from app.main import app
    from app.providers.notifications.base import NotificationDeliveryStatusResult

    ctx = await create_tenant_with_user(db_session, f"notif-poll-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)
    provider = FakeWhatsAppNotificationProvider(
        configured=True,
        status="sent",
        delivered=True,
        simulation_only=False,
        provider_reference="wa-poll-ref",
        polled_result=NotificationDeliveryStatusResult(
            delivery_stage="delivered",
            reconciliation_status="delivered",
            delivered=True,
            provider_message="Gateway poll confirmed final delivery.",
            external_status="delivered",
            terminal=True,
        ),
    )
    app.dependency_overrides[get_notification_providers] = lambda: [provider]

    try:
        dispatch = await client.post(
            "/api/v1/notifications/dispatch",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "whatsapp",
                "recipient": "+49123456789",
                "subject": "Polling check",
                "body": "Pending provider status.",
            },
        )
        polled = await client.post(
            "/api/v1/notifications/reconciliation/poll",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "whatsapp",
                "provider_reference": "wa-poll-ref",
            },
        )
        history = await client.get(
            "/api/v1/notifications/history",
            headers={"Authorization": f"Bearer {token}"},
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert dispatch.status_code == 200, dispatch.text
    assert polled.status_code == 200, polled.text
    assert polled.json()["updated"] is True
    assert provider.polled_references == ["wa-poll-ref"]
    assert history.status_code == 200, history.text
    row = history.json()[0]
    assert row["delivery_stage"] == "delivered"
    assert row["message"] == "Gateway poll confirmed final delivery."
    assert row["polling_supported"] is True


@pytest.mark.asyncio
async def test_poll_rejects_channel_without_polling_support(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    from app.core.dependencies import get_notification_providers
    from app.main import app

    ctx = await create_tenant_with_user(db_session, f"notif-poll-lock-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)
    app.dependency_overrides[get_notification_providers] = lambda: [
        FakeEmailNotificationProvider(
            configured=True,
            status="sent",
            delivered=True,
            simulation_only=False,
            provider_reference="email-poll-ref",
        )
    ]

    try:
        dispatch = await client.post(
            "/api/v1/notifications/dispatch",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "email",
                "recipient": "ops@example.org",
                "subject": "Polling unsupported",
                "body": "Email polling should stay unsupported in this sprint.",
            },
        )
        polled = await client.post(
            "/api/v1/notifications/reconciliation/poll",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "email",
                "provider_reference": "email-poll-ref",
            },
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert dispatch.status_code == 200, dispatch.text
    assert polled.status_code == 400
    assert "does not support reconciliation polling" in polled.json()["detail"]


@pytest.mark.asyncio
async def test_provider_callback_rejects_invalid_reconciliation_token(
    client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch,
) -> None:
    from app.core.config import settings

    monkeypatch.setattr(settings, "notification_reconciliation_callback_token", "callback-secret")
    ctx = await create_tenant_with_user(db_session, f"notif-callback-lock-{_uuid.uuid4().hex[:6]}")

    response = await client.post(
        "/api/v1/notifications/reconciliation/callback",
        headers={"X-Kairo-Notification-Token": "wrong-secret"},
        json={
            "tenant_id": str(ctx["tenant"].id),
            "channel": "email",
            "provider_reference": "missing-ref",
            "delivery_stage": "failed",
            "provider_message": "Rejected.",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid notification reconciliation token"


@pytest.mark.asyncio
async def test_live_dispatch_rejects_simulation_only_channel(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    from app.core.dependencies import get_notification_providers
    from app.main import app

    ctx = await create_tenant_with_user(db_session, f"notif-live-lock-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)
    app.dependency_overrides[get_notification_providers] = lambda: [
        FakeEmailNotificationProvider(
            configured=True,
            status="sent",
            delivered=True,
            simulation_only=False,
        ),
        _FakeSimulationProvider("telegram", "Telegram"),
        _FakeSimulationProvider("whatsapp", "WhatsApp"),
    ]

    try:
        response = await client.post(
            "/api/v1/notifications/dispatch",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "telegram",
                "recipient": "@ops-channel",
                "subject": "Telegram should stay simulated",
                "body": "No live telegram dispatch yet.",
            },
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert response.status_code == 400
    assert "only supports simulation" in response.json()["detail"]


@pytest.mark.asyncio
async def test_principal_admin_can_send_live_email_notification(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    from app.core.dependencies import get_notification_providers
    from app.main import app

    ctx = await create_tenant_with_user(db_session, f"notif-principal-live-{_uuid.uuid4().hex[:6]}")
    principal = await create_user_for_tenant(
        db_session,
        tenant_id=ctx["tenant"].id,
        email=f"principal-live-{_uuid.uuid4().hex[:6]}@test.org",
        password="PrincipalPass1!",
        display_name="Principal Admin",
        role_code="principal_admin",
        profile_type="admin",
    )
    await db_session.commit()
    token = await login(client, principal["user"].email, principal["password"], tenant_slug=ctx["tenant"].slug)
    provider = FakeEmailNotificationProvider(
        configured=True,
        status="sent",
        delivered=True,
        simulation_only=False,
        message="SMTP accepted the principal-admin notification.",
    )
    app.dependency_overrides[get_notification_providers] = lambda: [provider]

    try:
        response = await client.post(
            "/api/v1/notifications/dispatch",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "email",
                "recipient": "ops@example.org",
                "subject": "Principal admin notification",
                "body": "This validates principal-admin access to the live email dispatch path.",
            },
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_admin_can_send_live_telegram_notification_when_provider_is_live_capable(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    from app.core.dependencies import get_notification_providers
    from app.main import app

    ctx = await create_tenant_with_user(db_session, f"notif-telegram-live-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)
    provider = FakeTelegramNotificationProvider(
        configured=True,
        status="sent",
        delivered=True,
        simulation_only=False,
        message="Telegram accepted the operator notification.",
    )
    app.dependency_overrides[get_notification_providers] = lambda: [
        FakeEmailNotificationProvider(
            configured=True,
            status="sent",
            delivered=True,
            simulation_only=False,
        ),
        provider,
        _FakeSimulationProvider("whatsapp", "WhatsApp"),
    ]

    try:
        response = await client.post(
            "/api/v1/notifications/dispatch",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "telegram",
                "recipient": "@kairo_ops",
                "subject": "Kairo live telegram",
                "body": "This Telegram message validates the live operator notification path.",
            },
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["channel"] == "telegram"
    assert body["status"] == "sent"
    assert body["delivered"] is True
    assert body["simulation_only"] is False
    assert provider.calls[0]["tenant_id"] == str(ctx["tenant"].id)
    assert provider.calls[0]["recipient"] == "@kairo_ops"


@pytest.mark.asyncio
async def test_principal_admin_can_send_live_telegram_notification(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    from app.core.dependencies import get_notification_providers
    from app.main import app

    ctx = await create_tenant_with_user(db_session, f"notif-principal-telegram-{_uuid.uuid4().hex[:6]}")
    principal = await create_user_for_tenant(
        db_session,
        tenant_id=ctx["tenant"].id,
        email=f"principal-telegram-{_uuid.uuid4().hex[:6]}@test.org",
        password="PrincipalPass1!",
        display_name="Principal Admin",
        role_code="principal_admin",
        profile_type="admin",
    )
    await db_session.commit()
    token = await login(client, principal["user"].email, principal["password"], tenant_slug=ctx["tenant"].slug)
    provider = FakeTelegramNotificationProvider(
        configured=True,
        status="sent",
        delivered=True,
        simulation_only=False,
        message="Telegram accepted the principal-admin notification.",
    )
    app.dependency_overrides[get_notification_providers] = lambda: [provider]

    try:
        response = await client.post(
            "/api/v1/notifications/dispatch",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "telegram",
                "recipient": "@principal_ops",
                "subject": "Principal admin Telegram notification",
                "body": "This validates principal-admin access to the live Telegram dispatch path.",
            },
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_admin_can_send_live_whatsapp_notification_when_provider_is_live_capable(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    from app.core.dependencies import get_notification_providers
    from app.main import app

    ctx = await create_tenant_with_user(db_session, f"notif-whatsapp-live-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)
    provider = FakeWhatsAppNotificationProvider(
        configured=True,
        status="sent",
        delivered=True,
        simulation_only=False,
        message="WhatsApp accepted the operator notification.",
    )
    app.dependency_overrides[get_notification_providers] = lambda: [
        FakeEmailNotificationProvider(
            configured=True,
            status="sent",
            delivered=True,
            simulation_only=False,
        ),
        FakeTelegramNotificationProvider(
            configured=True,
            status="sent",
            delivered=True,
            simulation_only=False,
        ),
        provider,
    ]

    try:
        response = await client.post(
            "/api/v1/notifications/dispatch",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "whatsapp",
                "recipient": "+49123456789",
                "subject": "Kairo live WhatsApp",
                "body": "This WhatsApp message validates the live operator notification path.",
            },
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["channel"] == "whatsapp"
    assert body["status"] == "sent"
    assert body["delivered"] is True
    assert body["simulation_only"] is False
    assert provider.calls[0]["tenant_id"] == str(ctx["tenant"].id)
    assert provider.calls[0]["recipient"] == "+49123456789"


@pytest.mark.asyncio
async def test_principal_admin_can_send_live_whatsapp_notification(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    from app.core.dependencies import get_notification_providers
    from app.main import app

    ctx = await create_tenant_with_user(db_session, f"notif-principal-whatsapp-{_uuid.uuid4().hex[:6]}")
    principal = await create_user_for_tenant(
        db_session,
        tenant_id=ctx["tenant"].id,
        email=f"principal-whatsapp-{_uuid.uuid4().hex[:6]}@test.org",
        password="PrincipalPass1!",
        display_name="Principal Admin",
        role_code="principal_admin",
        profile_type="admin",
    )
    await db_session.commit()
    token = await login(client, principal["user"].email, principal["password"], tenant_slug=ctx["tenant"].slug)
    provider = FakeWhatsAppNotificationProvider(
        configured=True,
        status="sent",
        delivered=True,
        simulation_only=False,
        message="WhatsApp accepted the principal-admin notification.",
    )
    app.dependency_overrides[get_notification_providers] = lambda: [provider]

    try:
        response = await client.post(
            "/api/v1/notifications/dispatch",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "whatsapp",
                "recipient": "+33987654321",
                "subject": "Principal admin WhatsApp notification",
                "body": "This validates principal-admin access to the live WhatsApp dispatch path.",
            },
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert response.status_code == 200, response.text
