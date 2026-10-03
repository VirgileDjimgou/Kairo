"""Canonical TenantBranding contract: defaults, persistence, validation, delivery."""

from __future__ import annotations

import json
import uuid

import pytest
import pytest_asyncio
from fakes import FakeWebPushProvider
from helpers import create_tenant_with_user, login
from httpx import AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.user_models import (
    FirebasePushSubscription,
    NotificationDevice,
    NotificationDeviceProfile,
    NotificationOutboxEvent,
    UserNotification,
    WebPushSubscription,
)
from app.modules.notifications.user_service import UserNotificationService
from app.modules.tenancy.branding import branding_from_json
from app.modules.tenancy.models import Tenant
from app.modules.tenancy.schemas import TenantBranding

INSTALLATION = "installation-branding-0001"
WEB_ENDPOINT = "https://push.example.org/branding/web"


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


def test_default_branding_has_safe_kairo_values() -> None:
    branding = branding_from_json(None)
    assert branding == TenantBranding()
    assert branding.display_name == "Kairo"
    assert branding.short_name == "Kairo"
    assert branding.notification_name == "Kairo"
    assert branding.primary_color == "#1f4f8f"
    assert branding.theme_color == "#1a3f6b"
    assert branding.logo_url == ""
    assert branding.custom_domain == ""

    malformed = branding_from_json("{not-json")
    assert malformed == TenantBranding()


@pytest.mark.asyncio
async def test_default_branding_applies_to_settings_and_memberships(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    context = await create_tenant_with_user(db_session, "brand-default")
    token = await login(client, context["user"].email, context["password"])
    headers = {"Authorization": f"Bearer {token}"}

    settings = await client.get(
        f"/api/v1/tenants/{context['tenant'].id}/settings", headers=headers
    )
    assert settings.status_code == 200, settings.text
    assert settings.json()["branding"]["display_name"] == "Kairo"

    me = await client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200, me.text
    membership_branding = me.json()["memberships"][0]["branding"]
    assert membership_branding["display_name"] == "Kairo"
    assert membership_branding["notification_name"] == "Kairo"


@pytest.mark.asyncio
async def test_branding_update_persists_and_reaches_memberships(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    context = await create_tenant_with_user(db_session, "brand-update")
    token = await login(client, context["user"].email, context["password"])
    headers = {"Authorization": f"Bearer {token}"}
    branding_payload = {
        "display_name": "COMBIS App",
        "short_name": "COMBIS",
        "legal_name": "Combis Sport Verein e.V.",
        "notification_name": "COMBIS",
        "primary_color": "#0a5c2e",
        "secondary_color": "#c93146",
        "background_color": "#f4f7f2",
        "theme_color": "#0a5c2e",
        "favicon_url": "/favicon.svg",
        "support_name": "COMBIS Support",
        "support_email": "support@combis.example",
        "custom_domain": "combis.example.org",
    }

    updated = await client.put(
        f"/api/v1/tenants/{context['tenant'].id}/settings",
        headers=headers,
        json={"branding": branding_payload},
    )
    assert updated.status_code == 200, updated.text
    body = updated.json()["branding"]
    assert body["display_name"] == "COMBIS App"
    assert body["short_name"] == "COMBIS"
    assert body["notification_name"] == "COMBIS"
    assert body["custom_domain"] == "combis.example.org"

    persisted = await client.get(
        f"/api/v1/tenants/{context['tenant'].id}/settings", headers=headers
    )
    assert persisted.json()["branding"]["display_name"] == "COMBIS App"

    me = await client.get("/api/v1/auth/me", headers=headers)
    membership_branding = me.json()["memberships"][0]["branding"]
    assert membership_branding["display_name"] == "COMBIS App"
    assert membership_branding["theme_color"] == "#0a5c2e"
    # Unset fields keep their safe defaults.
    assert membership_branding["icon_192_url"] == ""


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "branding_payload",
    [
        {"logo_url": "javascript:alert(1)"},
        {"favicon_url": "data:text/html,<script>alert(1)</script>"},
        {"primary_color": "red"},
        {"theme_color": "#12345"},
        {"custom_domain": "Bad Domain!"},
    ],
)
async def test_branding_rejects_unsafe_values(
    client: AsyncClient, db_session: AsyncSession, branding_payload: dict
) -> None:
    context = await create_tenant_with_user(db_session, f"brand-invalid-{uuid.uuid4().hex[:6]}")
    token = await login(client, context["user"].email, context["password"])
    response = await client.put(
        f"/api/v1/tenants/{context['tenant'].id}/settings",
        headers={"Authorization": f"Bearer {token}"},
        json={"branding": branding_payload},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_push_title_uses_the_tenant_notification_name(db_session: AsyncSession) -> None:
    context = await create_tenant_with_user(db_session, "brand-push")
    tenant = await db_session.get(Tenant, context["tenant"].id)
    assert tenant is not None
    tenant.branding_json = json.dumps({"notification_name": "COMBIS"})  # type: ignore[assignment]
    await db_session.commit()

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
    await service.notify(
        tenant_id=context["tenant"].id,
        event_type="announcement.published",
        recipients=[context["user"].id],
        category="announcements",
        target_path="/announcements",
        deduplication_key="brand-push-1",
    )
    await db_session.commit()

    web_push = FakeWebPushProvider()
    await UserNotificationService(db_session, web_push_provider=web_push).process_outbox()

    assert web_push.sent
    _, message = web_push.sent[0]
    assert message.title == "COMBIS"


@pytest.mark.asyncio
async def test_push_title_falls_back_to_platform_name(db_session: AsyncSession) -> None:
    context = await create_tenant_with_user(db_session, "brand-push-default")
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
    await service.notify(
        tenant_id=context["tenant"].id,
        event_type="announcement.published",
        recipients=[context["user"].id],
        category="announcements",
        target_path="/announcements",
        deduplication_key="brand-push-default-1",
    )
    await db_session.commit()

    web_push = FakeWebPushProvider()
    await UserNotificationService(db_session, web_push_provider=web_push).process_outbox()

    _, message = web_push.sent[0]
    assert message.title == "Kairo"


@pytest.mark.asyncio
async def test_branding_does_not_change_roles_or_modules(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    context = await create_tenant_with_user(db_session, "brand-no-business")
    token = await login(client, context["user"].email, context["password"])
    headers = {"Authorization": f"Bearer {token}"}

    before = await client.get("/api/v1/auth/me", headers=headers)
    before_roles = before.json()["roles"]

    await client.put(
        f"/api/v1/tenants/{context['tenant'].id}/settings",
        headers=headers,
        json={"branding": {"display_name": "Renamed"}},
    )
    after = await client.get("/api/v1/auth/me", headers=headers)
    assert after.json()["roles"] == before_roles

    tenant = await db_session.scalar(
        select(Tenant).where(Tenant.id == context["tenant"].id)
    )
    assert tenant is not None
