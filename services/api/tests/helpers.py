"""Shared helpers for API integration tests."""

import uuid as _uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.identity.models import User
from app.modules.tenancy.models import Role, Tenant, TenantUser, user_roles


async def login(
    client: AsyncClient,
    email: str,
    password: str,
    tenant_slug: str | None = None,
) -> str:
    payload: dict = {"email": email, "password": password}
    if tenant_slug:
        payload["tenant_slug"] = tenant_slug
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


async def create_tenant_with_user(
    db: AsyncSession,
    slug_suffix: str,
    password: str = "TestIsolation1!",
    *,
    role_code: str = "admin",
    profile_type: str = "admin",
) -> dict:
    tenant = Tenant(
        id=_uuid.uuid4(),
        slug=f"docs-{slug_suffix}",
        name=f"Org {slug_suffix}",
    )
    db.add(tenant)
    await db.flush()

    user = User(
        id=_uuid.uuid4(),
        email=f"docs-{slug_suffix}@test.org",
        password_hash=hash_password(password),
        display_name=f"User {slug_suffix}",
        status="active",
    )
    db.add(user)
    await db.flush()

    role = Role(
        id=_uuid.uuid4(),
        tenant_id=tenant.id,
        code=role_code,
        name="Administrator" if role_code == "admin" else "Member",
        is_system_role=role_code == "admin",
    )
    db.add(role)
    await db.flush()

    membership = TenantUser(
        id=_uuid.uuid4(),
        tenant_id=tenant.id,
        user_id=user.id,
        profile_type=profile_type,
        membership_status="active",
    )
    db.add(membership)
    await db.flush()

    await db.execute(
        user_roles.insert().values(tenant_user_id=membership.id, role_id=role.id)
    )
    await db.flush()

    return {"tenant": tenant, "user": user, "password": password}
