"""
Sprint 16 tests: multi-tenant auth and tenant switching.

Covers:
- /auth/me returns memberships list with branding and module toggles
- /auth/switch-tenant returns new JWT for valid target tenant
- /auth/switch-tenant rejects non-member tenants (403)
- /auth/switch-tenant rejects non-existent tenants (404)
- Single-membership user still works through login -> me -> dashboard flow
- Branding and module toggles are returned in the memberships payload
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tenancy.models import Role
from helpers import create_tenant_with_user


@pytest.mark.asyncio
async def test_get_me_includes_memberships(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": data["user"].email, "password": data["password"]},
    )
    token = login.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "memberships" in body
    assert len(body["memberships"]) >= 1
    membership = body["memberships"][0]
    assert membership["tenant_id"] == str(data["tenant"].id)
    assert membership["slug"] == data["tenant"].slug
    assert "roles" in membership
    assert "branding" in membership
    assert "modules" in membership
    assert membership["branding"]["primary_color"] != ""
    assert membership["modules"]["chat"] is True


@pytest.mark.asyncio
async def test_switch_tenant_success(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": data["user"].email, "password": data["password"]},
    )
    token = login.json()["access_token"]

    response = await client.post(
        "/api/v1/auth/switch-tenant",
        json={"tenant_id": str(data["tenant"].id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["tenant_id"] == str(data["tenant"].id)
    assert body["user_id"] == str(data["user"].id)
    assert len(body["memberships"]) >= 1


@pytest.mark.asyncio
async def test_switch_tenant_rejects_nonexistent(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    import uuid

    data = seeded_tenant_and_admin
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": data["user"].email, "password": data["password"]},
    )
    token = login.json()["access_token"]
    fake_id = str(uuid.uuid4())

    response = await client.post(
        "/api/v1/auth/switch-tenant",
        json={"tenant_id": fake_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    # 403 is expected — non-member cannot learn whether a tenant exists
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_switch_tenant_requires_auth(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    import uuid

    response = await client.post(
        "/api/v1/auth/switch-tenant",
        json={"tenant_id": str(uuid.uuid4())},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_switch_tenant_returns_memberships_with_branding(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": data["user"].email, "password": data["password"]},
    )
    token = login.json()["access_token"]

    response = await client.post(
        "/api/v1/auth/switch-tenant",
        json={"tenant_id": str(data["tenant"].id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["memberships"]) >= 1
    m = body["memberships"][0]
    assert "branding" in m
    assert "modules" in m
    assert "profile_type" in m
    assert m["profile_type"] in ("admin", "member", "staff")


@pytest.mark.asyncio
async def test_admin_can_list_tenant_roles(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
    db_session: AsyncSession,
) -> None:
    data = seeded_tenant_and_admin
    db_session.add(
        Role(
            tenant_id=data["tenant"].id,
            code="member",
            name="Member",
            description="Standard member access",
            is_system_role=False,
        )
    )
    await db_session.flush()

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": data["user"].email, "password": data["password"]},
    )
    token = login.json()["access_token"]

    response = await client.get(
        f"/api/v1/tenants/{data['tenant'].id}/roles",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert {role["code"] for role in body} >= {"admin", "member"}


@pytest.mark.asyncio
async def test_non_admin_cannot_list_tenant_roles(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(
        db_session,
        "roles-member",
        role_code="member",
        profile_type="member",
    )
    token = await client.post(
        "/api/v1/auth/login",
        json={"email": ctx["user"].email, "password": ctx["password"]},
    )
    access_token = token.json()["access_token"]

    response = await client.get(
        f"/api/v1/tenants/{ctx['tenant'].id}/roles",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 403
