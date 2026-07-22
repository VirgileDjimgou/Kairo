import pytest
from fakes import FakeEmailNotificationProvider
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from test_identity_lifecycle import _create_member_role, _login_as_admin

from app.core.config import settings


@pytest.mark.asyncio
async def test_invite_hides_raw_token_when_email_is_sent_in_production(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.core.dependencies import get_notification_providers
    from app.main import app

    data = seeded_tenant_and_admin
    await _create_member_role(db_session, data["tenant"].id)
    auth_token = await _login_as_admin(client, data)
    provider = FakeEmailNotificationProvider(
        status="sent",
        delivered=True,
        simulation_only=False,
        message="SMTP accepted the invitation email.",
    )
    monkeypatch.setattr(settings, "app_env", "production")
    app.dependency_overrides[get_notification_providers] = lambda: [provider]

    try:
        response = await client.post(
            "/api/v1/auth/invite",
            json={
                "email": "live-delivery@example.org",
                "role_code": "member",
                "tenant_id": str(data["tenant"].id),
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["delivery_status"] == "sent"
    assert body["delivery_simulation_only"] is False
    assert body["invite_token"] is None
    assert provider.calls[0]["tenant_id"] == str(data["tenant"].id)
    assert provider.calls[0]["recipient"] == "live-delivery@example.org"


@pytest.mark.asyncio
async def test_invite_keeps_manual_fallback_when_delivery_fails(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.core.dependencies import get_notification_providers
    from app.main import app

    data = seeded_tenant_and_admin
    await _create_member_role(db_session, data["tenant"].id)
    auth_token = await _login_as_admin(client, data)
    provider = FakeEmailNotificationProvider(
        status="failed",
        delivered=False,
        simulation_only=False,
        message="SMTP relay rejected the message.",
    )
    monkeypatch.setattr(settings, "app_env", "production")
    app.dependency_overrides[get_notification_providers] = lambda: [provider]

    try:
        response = await client.post(
            "/api/v1/auth/invite",
            json={
                "email": "delivery-failure@example.org",
                "role_code": "member",
                "tenant_id": str(data["tenant"].id),
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["delivery_status"] == "failed"
    assert body["delivery_simulation_only"] is False
    assert body["invite_token"] is not None
    assert len(body["invite_token"]) > 20
    assert provider.calls[0]["tenant_id"] == str(data["tenant"].id)


@pytest.mark.asyncio
async def test_forgot_password_hides_token_when_email_is_sent_in_production(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.core.dependencies import get_notification_providers
    from app.main import app

    data = seeded_tenant_and_admin
    provider = FakeEmailNotificationProvider(
        status="sent",
        delivered=True,
        simulation_only=False,
        message="SMTP accepted the password reset email.",
    )
    monkeypatch.setattr(settings, "app_env", "production")
    app.dependency_overrides[get_notification_providers] = lambda: [provider]

    try:
        response = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": data["user"].email},
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["reset_token"] is None
    assert provider.calls[0]["tenant_id"] == str(data["tenant"].id)
    assert provider.calls[0]["recipient"] == data["user"].email


@pytest.mark.asyncio
async def test_forgot_password_keeps_token_in_simulation_mode(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.core.dependencies import get_notification_providers
    from app.main import app

    data = seeded_tenant_and_admin
    provider = FakeEmailNotificationProvider(
        status="simulated",
        delivered=False,
        simulation_only=True,
        message="Email simulation mode active.",
    )
    monkeypatch.setattr(settings, "app_env", "production")
    app.dependency_overrides[get_notification_providers] = lambda: [provider]

    try:
        response = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": data["user"].email},
        )
    finally:
        app.dependency_overrides.pop(get_notification_providers, None)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["reset_token"] is not None
    assert len(body["reset_token"]) > 20
    assert provider.calls[0]["tenant_id"] == str(data["tenant"].id)
