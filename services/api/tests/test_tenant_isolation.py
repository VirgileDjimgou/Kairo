"""
Sprint 1 security tests: tenant isolation.

Verifies that users from tenant A cannot access data belonging to tenant B.
This is the core multi-tenant security requirement.
"""

import pytest
import uuid as _uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.identity.models import User
from app.modules.tenancy.models import Role, Tenant, TenantUser, user_roles


async def _create_tenant_with_user(
    db: AsyncSession,
    slug_suffix: str,
    password: str = "TestIsolation1!",
) -> dict:
    """Helper: create an isolated tenant with one admin user."""
    tenant = Tenant(
        id=_uuid.uuid4(),
        slug=f"tenant-{slug_suffix}",
        name=f"Org {slug_suffix}",
    )
    db.add(tenant)
    await db.flush()

    user = User(
        id=_uuid.uuid4(),
        email=f"user-{slug_suffix}@test.org",
        password_hash=hash_password(password),
        display_name=f"User {slug_suffix}",
        status="active",
    )
    db.add(user)
    await db.flush()

    role = Role(
        id=_uuid.uuid4(),
        tenant_id=tenant.id,
        code="admin",
        name="Administrator",
        is_system_role=True,
    )
    db.add(role)
    await db.flush()

    membership = TenantUser(
        id=_uuid.uuid4(),
        tenant_id=tenant.id,
        user_id=user.id,
        profile_type="admin",
        membership_status="active",
    )
    db.add(membership)
    await db.flush()

    await db.execute(
        user_roles.insert().values(
            tenant_user_id=membership.id, role_id=role.id
        )
    )
    await db.flush()

    return {"tenant": tenant, "user": user, "password": password}


async def _login(client: AsyncClient, email: str, password: str) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_user_cannot_access_other_tenant(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    User from tenant A must NOT be able to access tenant B's data via /tenants/{id}.
    """
    alpha = await _create_tenant_with_user(db_session, f"alpha-{_uuid.uuid4().hex[:6]}")
    beta = await _create_tenant_with_user(db_session, f"beta-{_uuid.uuid4().hex[:6]}")

    token_alpha = await _login(
        client, alpha["user"].email, alpha["password"]
    )

    # Alpha user tries to access Beta tenant — must be forbidden
    response = await client.get(
        f"/api/v1/tenants/{beta['tenant'].id}",
        headers={"Authorization": f"Bearer {token_alpha}"},
    )
    assert response.status_code == 403, (
        f"Expected 403 but got {response.status_code}: {response.text}"
    )


@pytest.mark.asyncio
async def test_user_can_access_own_tenant(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """User can access their own tenant — baseline positive case."""
    data = await _create_tenant_with_user(db_session, f"own-{_uuid.uuid4().hex[:6]}")
    token = await _login(client, data["user"].email, data["password"])

    response = await client.get(
        f"/api/v1/tenants/{data['tenant'].id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(data["tenant"].id)
    assert body["slug"] == data["tenant"].slug


@pytest.mark.asyncio
async def test_tenant_list_only_returns_own_tenants(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    GET /tenants/ must only return tenants the user belongs to.
    Tenant B must NOT appear in Tenant A user's list.
    """
    alpha = await _create_tenant_with_user(db_session, f"list-a-{_uuid.uuid4().hex[:6]}")
    # Create tenant B (different user)
    await _create_tenant_with_user(db_session, f"list-b-{_uuid.uuid4().hex[:6]}")

    token_alpha = await _login(client, alpha["user"].email, alpha["password"])

    response = await client.get(
        "/api/v1/tenants/",
        headers={"Authorization": f"Bearer {token_alpha}"},
    )
    assert response.status_code == 200
    tenant_ids = [t["id"] for t in response.json()]

    # Alpha user sees only their own tenant
    assert str(alpha["tenant"].id) in tenant_ids

    # No other tenants leak into the response
    assert len(tenant_ids) == 1, (
        f"Expected 1 tenant but got {len(tenant_ids)}: {tenant_ids}"
    )


@pytest.mark.asyncio
async def test_inactive_user_cannot_login(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Disabled accounts must not receive a JWT."""
    tenant = Tenant(id=_uuid.uuid4(), slug=f"inactive-{_uuid.uuid4().hex[:6]}", name="Test")
    db_session.add(tenant)
    await db_session.flush()

    user = User(
        id=_uuid.uuid4(),
        email=f"disabled-{_uuid.uuid4().hex[:6]}@test.org",
        password_hash=hash_password("Pass123!"),
        display_name="Disabled User",
        status="disabled",  # <-- inactive
    )
    db_session.add(user)
    await db_session.flush()

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "Pass123!"},
    )
    assert response.status_code in (401, 403)
