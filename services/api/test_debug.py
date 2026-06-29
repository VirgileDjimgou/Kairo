"""Debug script — run with: pytest test_debug.py -x -s"""
import uuid as _uuid
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def _auth_headers(client, user, tenant):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "TestPass123!", "tenant_id": str(tenant.id)},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_debug_events_export(client: AsyncClient, db_session):
    from app.core.security import hash_password
    from app.modules.identity.models import User
    from app.modules.tenancy.models import Role, Tenant, TenantUser, user_roles

    tenant = Tenant(
        id=_uuid.uuid4(),
        slug=f"debug-{_uuid.uuid4().hex[:8]}",
        name="Debug",
        type="association",
    )
    db_session.add(tenant)
    await db_session.flush()

    user = User(
        id=_uuid.uuid4(),
        email=f"debug-admin-{_uuid.uuid4().hex[:6]}@test.org",
        password_hash=hash_password("TestPass123!"),
        display_name="Debug Admin",
        status="active",
    )
    db_session.add(user)
    await db_session.flush()

    role = Role(
        id=_uuid.uuid4(), tenant_id=tenant.id, code="admin", name="Administrator", is_system_role=True,
    )
    db_session.add(role)
    await db_session.flush()

    membership = TenantUser(
        id=_uuid.uuid4(), tenant_id=tenant.id, user_id=user.id, profile_type="admin", membership_status="active",
    )
    db_session.add(membership)
    await db_session.flush()
    await db_session.execute(user_roles.insert().values(tenant_user_id=membership.id, role_id=role.id))
    await db_session.flush()

    headers = await _auth_headers(client, user, tenant)

    # Create event
    from datetime import datetime, timezone
    resp = await client.post(
        "/api/v1/events/",
        headers=headers,
        json={"title": "Test Event", "start_at": datetime.now(timezone.utc).isoformat(), "visibility_scope": "members_only", "status": "published"},
    )
    print(f"Create event: {resp.status_code} {resp.text[:200]}")

    # Export event
    resp2 = await client.get("/api/v1/events/export", headers=headers)
    print(f"Export events: {resp2.status_code}")
    print(f"Export headers: {dict(resp2.headers)}")
    print(f"Export text: {resp2.text[:500]}")
