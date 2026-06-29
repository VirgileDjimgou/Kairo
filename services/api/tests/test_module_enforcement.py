import json
import uuid as _uuid

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


def _disabled_settings(**kwargs) -> str:
    toggles = {
        "membership": True,
        "contributions": True,
        "policies": True,
        "disciplinary": True,
        "events": True,
        "announcements": True,
        "chat": True,
        "notifications": True,
    }
    toggles.update(kwargs)
    return json.dumps({"modules": toggles})


async def _create_tenant(db_session, settings_json: str):
    from app.modules.tenancy.models import Tenant
    tenant = Tenant(
        id=_uuid.uuid4(),
        slug=f"modtest-{_uuid.uuid4().hex[:8]}",
        name="Module Test Org",
        type="association",
        settings_json=settings_json,
    )
    db_session.add(tenant)
    await db_session.flush()
    return tenant


async def _create_admin(db_session, tenant):
    from app.core.security import hash_password
    from app.modules.identity.models import User
    from app.modules.tenancy.models import Role, TenantUser, user_roles
    user = User(
        id=_uuid.uuid4(),
        email=f"admin-{_uuid.uuid4().hex[:6]}@modtest.org",
        password_hash=hash_password("TestPass123!"),
        display_name="Mod Test Admin",
        status="active",
    )
    db_session.add(user)
    await db_session.flush()
    role = Role(
        id=_uuid.uuid4(),
        tenant_id=tenant.id,
        code="admin",
        name="Administrator",
        is_system_role=True,
    )
    db_session.add(role)
    await db_session.flush()
    membership = TenantUser(
        id=_uuid.uuid4(),
        tenant_id=tenant.id,
        user_id=user.id,
        profile_type="admin",
        membership_status="active",
    )
    db_session.add(membership)
    await db_session.flush()
    await db_session.execute(
        user_roles.insert().values(tenant_user_id=membership.id, role_id=role.id)
    )
    await db_session.flush()
    return user, tenant


async def _login(client: AsyncClient, user_email: str, tenant_id: str) -> str:
    resp = await client.post(
        "/api/v1/auth/login",
        json={
            "email": user_email,
            "password": "TestPass123!",
            "tenant_id": tenant_id,
        },
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


class TestModuleEnforcement:

    async def test_chat_disabled_returns_403(self, client: AsyncClient, db_session):
        tenant = await _create_tenant(db_session, _disabled_settings(chat=False))
        user, _ = await _create_admin(db_session, tenant)
        token = await _login(client, user.email, str(tenant.id))
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.post(
            "/api/v1/chat/query",
            headers=headers,
            json={"tenant_id": str(tenant.id), "question": "test", "conversation_id": None},
        )
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
        assert "chat" in resp.json()["detail"].lower()

    async def test_events_disabled_returns_403(self, client: AsyncClient, db_session):
        tenant = await _create_tenant(db_session, _disabled_settings(events=False))
        user, _ = await _create_admin(db_session, tenant)
        token = await _login(client, user.email, str(tenant.id))
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.get("/api/v1/events/public", headers=headers)
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
        assert "events" in resp.json()["detail"].lower()

    async def test_enabled_module_allows_access(self, client: AsyncClient, db_session):
        tenant = await _create_tenant(db_session, _disabled_settings(events=True, chat=False))
        user, _ = await _create_admin(db_session, tenant)
        token = await _login(client, user.email, str(tenant.id))
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.get("/api/v1/events/public", headers=headers)
        assert resp.status_code != 403, f"Events should be accessible: {resp.text}"

    async def test_chat_disabled_in_admin_queries(self, client: AsyncClient, db_session):
        tenant = await _create_tenant(db_session, _disabled_settings(chat=False))
        user, _ = await _create_admin(db_session, tenant)
        token = await _login(client, user.email, str(tenant.id))
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.get("/api/v1/admin/chat-queries?limit=10", headers=headers)
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
        assert "chat" in resp.json()["detail"].lower()

    async def test_membership_disabled_returns_403(self, client: AsyncClient, db_session):
        tenant = await _create_tenant(db_session, _disabled_settings(membership=False))
        user, _ = await _create_admin(db_session, tenant)
        token = await _login(client, user.email, str(tenant.id))
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.get("/api/v1/memberships/profile", headers=headers)
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
        assert "membership" in resp.json()["detail"].lower()

    async def test_multiple_disabled_membership_enabled(
        self, client: AsyncClient, db_session
    ):
        tenant = await _create_tenant(
            db_session, _disabled_settings(chat=False, events=False, membership=True)
        )
        user, _ = await _create_admin(db_session, tenant)
        token = await _login(client, user.email, str(tenant.id))
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.get("/api/v1/memberships/profile", headers=headers)
        assert resp.status_code != 403, f"Membership should be accessible: {resp.text}"
