"""
Sprint 17 tests: identity lifecycle and access hardening.

Covers:
- Invitation flow: create, accept, duplicate, expired, cancel
- Password reset: forgot, reset, token expiry, token replay
- MFA: enroll, verify, login with MFA, disable
- Token refresh
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
import pyotp
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, hash_token
from app.modules.identity.models import Invitation, PasswordResetToken, User
from app.modules.tenancy.models import TenantUser, Role


# ── Helpers ────────────────────────────────────────────────────────────────────

async def _login_as_admin(client: AsyncClient, data: dict) -> str:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": data["user"].email, "password": data["password"]},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


async def _create_member_role(db_session: AsyncSession, tenant_id: uuid.UUID) -> Role:
    role = Role(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        code="member",
        name="Member",
        is_system_role=False,
    )
    db_session.add(role)
    await db_session.flush()
    return role


# ── Invitation Flow ────────────────────────────────────────────────────────────

class TestInvitationFlow:
    @pytest.mark.asyncio
    async def test_invite_creates_pending_invitation(
        self, client: AsyncClient, seeded_tenant_and_admin: dict,
        db_session: AsyncSession,
    ) -> None:
        data = seeded_tenant_and_admin
        await _create_member_role(db_session, data["tenant"].id)
        token = await _login_as_admin(client, data)

        resp = await client.post(
            "/api/v1/auth/invite",
            json={
                "email": "newuser@test.org",
                "role_code": "member",
                "tenant_id": str(data["tenant"].id),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["status"] == "pending"
        assert body["email"] == "newuser@test.org"
        assert body["role_code"] == "member"
        assert "invite_token" in body
        assert len(body["invite_token"]) > 20

    @pytest.mark.asyncio
    async def test_invite_requires_admin(
        self, client: AsyncClient, seeded_tenant_and_admin: dict,
        db_session: AsyncSession,
    ) -> None:
        from helpers import create_tenant_with_user
        data = seeded_tenant_and_admin
        member = await create_tenant_with_user(
            db_session, "member-only", role_code="member", profile_type="member"
        )
        member_token = await _login_as_admin(client, member)

        resp = await client.post(
            "/api/v1/auth/invite",
            json={
                "email": "another@test.org",
                "role_code": "member",
                "tenant_id": str(member["tenant"].id),
            },
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_invite_duplicate_email_rejected(
        self, client: AsyncClient, seeded_tenant_and_admin: dict,
        db_session: AsyncSession,
    ) -> None:
        data = seeded_tenant_and_admin
        await _create_member_role(db_session, data["tenant"].id)
        token = await _login_as_admin(client, data)

        # First invite
        await client.post(
            "/api/v1/auth/invite",
            json={
                "email": "duplicate@test.org",
                "role_code": "member",
                "tenant_id": str(data["tenant"].id),
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        # Second invite with same email
        resp = await client.post(
            "/api/v1/auth/invite",
            json={
                "email": "duplicate@test.org",
                "role_code": "member",
                "tenant_id": str(data["tenant"].id),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_accept_invite_creates_user_and_membership(
        self, client: AsyncClient, seeded_tenant_and_admin: dict,
        db_session: AsyncSession,
    ) -> None:
        data = seeded_tenant_and_admin
        await _create_member_role(db_session, data["tenant"].id)
        token = await _login_as_admin(client, data)

        invite_resp = await client.post(
            "/api/v1/auth/invite",
            json={
                "email": "acceptme@test.org",
                "role_code": "member",
                "tenant_id": str(data["tenant"].id),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert invite_resp.status_code == 201, invite_resp.text
        raw_token = invite_resp.json()["invite_token"]

        resp = await client.post(
            "/api/v1/auth/accept-invite",
            json={
                "token": raw_token,
                "display_name": "Accept Me",
                "password": "StrongPass123!",
            },
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "access_token" in body
        assert body["tenant_id"] == str(data["tenant"].id)

        # Verify we can use the new token
        me_resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {body['access_token']}"},
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "acceptme@test.org"

    @pytest.mark.asyncio
    async def test_accept_invite_rejects_expired_token(
        self, client: AsyncClient, seeded_tenant_and_admin: dict,
        db_session: AsyncSession,
    ) -> None:
        data = seeded_tenant_and_admin
        raw_token = "expired-test-token"
        token_hash_value = hash_token(raw_token)
        invitation = Invitation(
            id=uuid.uuid4(),
            tenant_id=data["tenant"].id,
            email="expired@test.org",
            role_code="member",
            invited_by_user_id=data["user"].id,
            token_hash=token_hash_value,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
            status="pending",
        )
        db_session.add(invitation)
        await db_session.flush()

        resp = await client.post(
            "/api/v1/auth/accept-invite",
            json={
                "token": raw_token,
                "display_name": "Expired User",
                "password": "StrongPass123!",
            },
        )
        assert resp.status_code == 400, resp.text
        assert "expired" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_accept_invite_rejects_invalid_token(
        self, client: AsyncClient
    ) -> None:
        for _ in range(5):
            resp = await client.post(
                "/api/v1/auth/accept-invite",
                json={
                    "token": "nonexistent-token",
                    "display_name": "Fake User",
                    "password": "StrongPass123!",
                },
            )
            assert resp.status_code == 404

        resp = await client.post(
            "/api/v1/auth/accept-invite",
            json={
                "token": "nonexistent-token",
                "display_name": "Fake User",
                "password": "StrongPass123!",
            },
        )
        assert resp.status_code == 429

    @pytest.mark.asyncio
    async def test_invite_existing_active_member_rejected(
        self, client: AsyncClient, seeded_tenant_and_admin: dict,
        db_session: AsyncSession,
    ) -> None:
        data = seeded_tenant_and_admin
        await _create_member_role(db_session, data["tenant"].id)
        admin_token = await _login_as_admin(client, data)

        resp = await client.post(
            "/api/v1/auth/invite",
            json={
                "email": data["user"].email,
                "role_code": "member",
                "tenant_id": str(data["tenant"].id),
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_cancel_invitation(
        self, client: AsyncClient, seeded_tenant_and_admin: dict,
        db_session: AsyncSession,
    ) -> None:
        data = seeded_tenant_and_admin
        await _create_member_role(db_session, data["tenant"].id)
        token = await _login_as_admin(client, data)

        invite_resp = await client.post(
            "/api/v1/auth/invite",
            json={
                "email": "cancelme@test.org",
                "role_code": "member",
                "tenant_id": str(data["tenant"].id),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert invite_resp.status_code == 201, invite_resp.text
        inv_id = invite_resp.json()["invitation_id"]

        resp = await client.delete(
            f"/api/v1/auth/invitations/{inv_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 204

        list_resp = await client.get(
            f"/api/v1/auth/invitations/{data['tenant'].id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert list_resp.status_code == 200
        invitations = list_resp.json()
        cancelled = [i for i in invitations if i["id"] == inv_id]
        assert len(cancelled) == 1
        assert cancelled[0]["status"] == "cancelled"


# ── Password Reset Flow ────────────────────────────────────────────────────────

class TestPasswordResetFlow:
    @pytest.mark.asyncio
    async def test_forgot_password_returns_token_for_existing_user(
        self, client: AsyncClient, seeded_tenant_and_admin: dict
    ) -> None:
        data = seeded_tenant_and_admin
        resp = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": data["user"].email},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["reset_token"] is not None
        assert len(body["reset_token"]) > 20

    @pytest.mark.asyncio
    async def test_forgot_password_non_enumeration(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "nonexistent@test.org"},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["reset_token"] is None

    @pytest.mark.asyncio
    async def test_reset_password_success(
        self, client: AsyncClient, seeded_tenant_and_admin: dict
    ) -> None:
        data = seeded_tenant_and_admin
        forgot_resp = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": data["user"].email},
        )
        reset_token = forgot_resp.json()["reset_token"]

        resp = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": reset_token, "new_password": "NewStrongPass456!"},
        )
        assert resp.status_code == 200, resp.text

        # Verify new password works
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": data["user"].email, "password": "NewStrongPass456!"},
        )
        assert login_resp.status_code == 200, login_resp.text

    @pytest.mark.asyncio
    async def test_reset_password_rate_limits_repeated_requests(
        self, client: AsyncClient, seeded_tenant_and_admin: dict
    ) -> None:
        data = seeded_tenant_and_admin
        forgot_resp = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": data["user"].email},
        )
        reset_token = forgot_resp.json()["reset_token"]

        for _ in range(5):
            resp = await client.post(
                "/api/v1/auth/reset-password",
                json={"token": reset_token, "new_password": "NewStrongPass456!"},
            )
            assert resp.status_code in {200, 400, 404}

        rate_limited = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": reset_token, "new_password": "NewStrongPass456!"},
        )
        assert rate_limited.status_code == 429

    @pytest.mark.asyncio
    async def test_reset_password_rejects_used_token(
        self, client: AsyncClient, seeded_tenant_and_admin: dict
    ) -> None:
        data = seeded_tenant_and_admin
        forgot_resp = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": data["user"].email},
        )
        reset_token = forgot_resp.json()["reset_token"]

        await client.post(
            "/api/v1/auth/reset-password",
            json={"token": reset_token, "new_password": "NewPass789!"},
        )

        resp = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": reset_token, "new_password": "AnotherPass123!"},
        )
        assert resp.status_code == 400, resp.text
        assert "already been used" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_reset_password_rejects_expired_token(
        self, client: AsyncClient, seeded_tenant_and_admin: dict,
        db_session: AsyncSession,
    ) -> None:
        data = seeded_tenant_and_admin
        raw_token = "expired-reset-token"
        token_hash_value = hash_token(raw_token)
        prt = PasswordResetToken(
            id=uuid.uuid4(),
            user_id=data["user"].id,
            token_hash=token_hash_value,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )
        db_session.add(prt)
        await db_session.flush()

        resp = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": raw_token, "new_password": "NewPass123!"},
        )
        assert resp.status_code == 400, resp.text
        assert "expired" in resp.json()["detail"].lower()


# ── MFA Flow ───────────────────────────────────────────────────────────────────

class TestMfaFlow:
    @pytest.mark.asyncio
    async def test_enroll_mfa_generates_secret(
        self, client: AsyncClient, seeded_tenant_and_admin: dict
    ) -> None:
        data = seeded_tenant_and_admin
        token = await _login_as_admin(client, data)

        resp = await client.post(
            "/api/v1/auth/mfa/enroll",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "secret" in body
        assert "uri" in body
        assert len(body["secret"]) > 10

    @pytest.mark.asyncio
    async def test_enroll_then_verify_and_enable_mfa(
        self, client: AsyncClient, seeded_tenant_and_admin: dict
    ) -> None:
        data = seeded_tenant_and_admin
        auth_token = await _login_as_admin(client, data)

        enroll_resp = await client.post(
            "/api/v1/auth/mfa/enroll",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        secret = enroll_resp.json()["secret"]

        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        resp = await client.post(
            "/api/v1/auth/mfa/verify",
            json={"code": valid_code},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["enabled"] is True

    @pytest.mark.asyncio
    async def test_login_triggers_mfa_when_enabled(
        self, client: AsyncClient, seeded_tenant_and_admin: dict
    ) -> None:
        data = seeded_tenant_and_admin
        auth_token = await _login_as_admin(client, data)

        # Enable MFA
        enroll_resp = await client.post(
            "/api/v1/auth/mfa/enroll",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        secret = enroll_resp.json()["secret"]
        totp = pyotp.TOTP(secret)
        verify_resp = await client.post(
            "/api/v1/auth/mfa/verify",
            json={"code": totp.now()},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert verify_resp.status_code == 200, verify_resp.text

        # Login should now return MFA challenge
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": data["user"].email, "password": data["password"]},
        )
        assert login_resp.status_code == 200, login_resp.text
        body = login_resp.json()
        assert body["mfa_required"] is True
        assert "mfa_token" in body

        # Complete MFA login
        mfa_code = pyotp.TOTP(secret).now()
        complete_resp = await client.post(
            "/api/v1/auth/mfa/complete",
            json={"mfa_token": body["mfa_token"], "code": mfa_code},
        )
        assert complete_resp.status_code == 200, complete_resp.text
        mfa_body = complete_resp.json()
        assert "access_token" in mfa_body
        assert str(data["user"].id) == mfa_body["user_id"]

    @pytest.mark.asyncio
    async def test_mfa_complete_with_invalid_code(
        self, client: AsyncClient, seeded_tenant_and_admin: dict
    ) -> None:
        data = seeded_tenant_and_admin
        auth_token = await _login_as_admin(client, data)

        # Enable MFA
        enroll_resp = await client.post(
            "/api/v1/auth/mfa/enroll",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        secret = enroll_resp.json()["secret"]
        totp = pyotp.TOTP(secret)
        await client.post(
            "/api/v1/auth/mfa/verify",
            json={"code": totp.now()},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Get MFA challenge
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": data["user"].email, "password": data["password"]},
        )
        mfa_token = login_resp.json().get("mfa_token")
        assert mfa_token is not None

        complete_resp = await client.post(
            "/api/v1/auth/mfa/complete",
            json={"mfa_token": mfa_token, "code": "000000"},
        )
        assert complete_resp.status_code == 401

    @pytest.mark.asyncio
    async def test_disable_mfa(
        self, client: AsyncClient, seeded_tenant_and_admin: dict
    ) -> None:
        data = seeded_tenant_and_admin
        auth_token = await _login_as_admin(client, data)

        # Enable MFA
        enroll_resp = await client.post(
            "/api/v1/auth/mfa/enroll",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        secret = enroll_resp.json()["secret"]
        totp = pyotp.TOTP(secret)
        await client.post(
            "/api/v1/auth/mfa/verify",
            json={"code": totp.now()},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Disable MFA
        resp = await client.delete(
            "/api/v1/auth/mfa",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert resp.status_code == 204

        # Login should now work without MFA
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": data["user"].email, "password": data["password"]},
        )
        assert login_resp.status_code == 200, login_resp.text
        assert "mfa_required" not in login_resp.json()


# ── Token Refresh ──────────────────────────────────────────────────────────────

class TestTokenRefresh:
    @pytest.mark.asyncio
    async def test_refresh_token_works(
        self, client: AsyncClient, seeded_tenant_and_admin: dict
    ) -> None:
        from app.core.security import create_refresh_token

        data = seeded_tenant_and_admin
        refresh = create_refresh_token(data["user"].id)

        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_rejects_invalid_token(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "not-a-valid-jwt"},
        )
        assert resp.status_code == 401


# ── Tenant Isolation ───────────────────────────────────────────────────────────

class TestTenantIsolation:
    @pytest.mark.asyncio
    async def test_invite_rejects_wrong_tenant(
        self, client: AsyncClient, seeded_tenant_and_admin: dict,
    ) -> None:
        data = seeded_tenant_and_admin
        token = await _login_as_admin(client, data)

        fake_tenant_id = str(uuid.uuid4())
        resp = await client.post(
            "/api/v1/auth/invite",
            json={
                "email": "cross-tenant@test.org",
                "role_code": "admin",
                "tenant_id": fake_tenant_id,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_accept_invite_creates_correct_tenant_membership(
        self, client: AsyncClient, seeded_tenant_and_admin: dict,
        db_session: AsyncSession,
    ) -> None:
        data = seeded_tenant_and_admin
        await _create_member_role(db_session, data["tenant"].id)
        token = await _login_as_admin(client, data)

        invite_resp = await client.post(
            "/api/v1/auth/invite",
            json={
                "email": "tenant-isolation@test.org",
                "role_code": "member",
                "tenant_id": str(data["tenant"].id),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert invite_resp.status_code == 201, invite_resp.text
        raw_token = invite_resp.json()["invite_token"]

        accept_resp = await client.post(
            "/api/v1/auth/accept-invite",
            json={
                "token": raw_token,
                "display_name": "Isolation Test",
                "password": "StrongPass123!",
            },
        )
        assert accept_resp.status_code == 200, accept_resp.text
        new_token = accept_resp.json()["access_token"]

        me_resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {new_token}"},
        )
        assert me_resp.status_code == 200, me_resp.text
        memberships = me_resp.json()["memberships"]
        assert len(memberships) == 1
        assert memberships[0]["tenant_id"] == str(data["tenant"].id)
