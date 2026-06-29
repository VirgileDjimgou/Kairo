import pytest
import pyotp
from httpx import AsyncClient

from app.core.security import create_refresh_token, decode_access_token


pytestmark = pytest.mark.asyncio


async def _login_access_token(
    client: AsyncClient,
    *,
    email: str,
    password: str,
    tenant_slug: str | None = None,
) -> str:
    payload: dict[str, str] = {"email": email, "password": password}
    if tenant_slug:
        payload["tenant_slug"] = tenant_slug
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200, response.text
    body = response.json()
    assert "access_token" in body
    return body["access_token"]


async def _login_with_mfa(
    client: AsyncClient,
    *,
    email: str,
    password: str,
    code: str,
    tenant_slug: str | None = None,
) -> str:
    payload: dict[str, str] = {"email": email, "password": password}
    if tenant_slug:
        payload["tenant_slug"] = tenant_slug
    login_response = await client.post("/api/v1/auth/login", json=payload)
    assert login_response.status_code == 200, login_response.text
    mfa_token = login_response.json()["mfa_token"]
    complete_response = await client.post(
        "/api/v1/auth/mfa/complete",
        json={"mfa_token": mfa_token, "code": code},
    )
    assert complete_response.status_code == 200, complete_response.text
    return complete_response.json()["access_token"]


async def test_session_inventory_and_targeted_revocation(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
) -> None:
    data = seeded_tenant_and_admin
    current_token = await _login_access_token(
        client,
        email=data["user"].email,
        password=data["password"],
        tenant_slug=data["tenant"].slug,
    )
    other_token = await _login_access_token(
        client,
        email=data["user"].email,
        password=data["password"],
        tenant_slug=data["tenant"].slug,
    )

    sessions_response = await client.get(
        "/api/v1/auth/sessions",
        headers={"Authorization": f"Bearer {current_token}"},
    )
    assert sessions_response.status_code == 200, sessions_response.text
    sessions = sessions_response.json()
    assert len(sessions) == 2
    current_session = next(session for session in sessions if session["current"] is True)
    other_session = next(session for session in sessions if session["current"] is False)
    assert current_session["id"] != other_session["id"]

    revoke_response = await client.delete(
        f"/api/v1/auth/sessions/{other_session['id']}",
        headers={"Authorization": f"Bearer {current_token}"},
    )
    assert revoke_response.status_code == 200, revoke_response.text
    assert revoke_response.json()["revoked_session_count"] == 1

    current_access = await client.get(
        "/api/v1/auth/protected",
        headers={"Authorization": f"Bearer {current_token}"},
    )
    assert current_access.status_code == 200, current_access.text

    other_access = await client.get(
        "/api/v1/auth/protected",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert other_access.status_code == 401, other_access.text


async def test_revoke_all_invalidates_current_session_and_refresh_token(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
) -> None:
    data = seeded_tenant_and_admin
    access_token = await _login_access_token(
        client,
        email=data["user"].email,
        password=data["password"],
        tenant_slug=data["tenant"].slug,
    )
    session_id = decode_access_token(access_token)["sid"]
    refresh_token = create_refresh_token(data["user"].id, session_id=session_id)

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200, refresh_response.text

    revoke_response = await client.post(
        "/api/v1/auth/sessions/revoke-all",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert revoke_response.status_code == 200, revoke_response.text
    assert revoke_response.json()["revoked_session_count"] >= 1

    protected_response = await client.get(
        "/api/v1/auth/protected",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert protected_response.status_code == 401, protected_response.text

    refresh_after_revoke = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_after_revoke.status_code == 401, refresh_after_revoke.text


async def test_password_reset_revokes_existing_sessions(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
) -> None:
    data = seeded_tenant_and_admin
    access_token = await _login_access_token(
        client,
        email=data["user"].email,
        password=data["password"],
        tenant_slug=data["tenant"].slug,
    )

    forgot_response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": data["user"].email},
    )
    assert forgot_response.status_code == 200, forgot_response.text
    reset_token = forgot_response.json()["reset_token"]
    assert reset_token is not None

    reset_response = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": "RotatedPass456!"},
    )
    assert reset_response.status_code == 200, reset_response.text

    old_session_response = await client.get(
        "/api/v1/auth/protected",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert old_session_response.status_code == 401, old_session_response.text

    new_login = await client.post(
        "/api/v1/auth/login",
        json={"email": data["user"].email, "password": "RotatedPass456!"},
    )
    assert new_login.status_code == 200, new_login.text


async def test_disabling_mfa_revokes_other_sessions_only(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
) -> None:
    data = seeded_tenant_and_admin
    current_token = await _login_access_token(
        client,
        email=data["user"].email,
        password=data["password"],
        tenant_slug=data["tenant"].slug,
    )

    enroll_response = await client.post(
        "/api/v1/auth/mfa/enroll",
        headers={"Authorization": f"Bearer {current_token}"},
    )
    assert enroll_response.status_code == 200, enroll_response.text
    secret = enroll_response.json()["secret"]
    verify_response = await client.post(
        "/api/v1/auth/mfa/verify",
        json={"code": pyotp.TOTP(secret).now()},
        headers={"Authorization": f"Bearer {current_token}"},
    )
    assert verify_response.status_code == 200, verify_response.text

    other_token = await _login_with_mfa(
        client,
        email=data["user"].email,
        password=data["password"],
        code=pyotp.TOTP(secret).now(),
        tenant_slug=data["tenant"].slug,
    )

    disable_response = await client.delete(
        "/api/v1/auth/mfa",
        headers={"Authorization": f"Bearer {current_token}"},
    )
    assert disable_response.status_code == 204, disable_response.text

    current_access = await client.get(
        "/api/v1/auth/protected",
        headers={"Authorization": f"Bearer {current_token}"},
    )
    assert current_access.status_code == 200, current_access.text

    other_access = await client.get(
        "/api/v1/auth/protected",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert other_access.status_code == 401, other_access.text


async def test_security_events_include_identity_activity(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
) -> None:
    data = seeded_tenant_and_admin
    access_token = await _login_access_token(
        client,
        email=data["user"].email,
        password=data["password"],
        tenant_slug=data["tenant"].slug,
    )
    await client.post(
        "/api/v1/auth/sessions/revoke-others",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    events_response = await client.get(
        "/api/v1/auth/security-events",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert events_response.status_code == 200, events_response.text
    actions = [event["action"] for event in events_response.json()]
    assert "login_succeeded" in actions
