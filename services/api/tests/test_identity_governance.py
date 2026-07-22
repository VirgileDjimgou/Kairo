import uuid

import pytest
from helpers import create_tenant_with_user
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_refresh_token, decode_access_token
from app.modules.identity.models import User
from app.modules.tenancy.models import Role, TenantUser, user_roles

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
    return response.json()["access_token"]


async def _attach_existing_user_to_tenant(
    db_session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user: User,
    role_id: uuid.UUID,
    profile_type: str = "member",
    membership_status: str = "active",
) -> TenantUser:
    membership = TenantUser(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        user_id=user.id,
        profile_type=profile_type,
        membership_status=membership_status,
    )
    db_session.add(membership)
    await db_session.flush()
    await db_session.execute(
        user_roles.insert().values(
            tenant_user_id=membership.id,
            role_id=role_id,
        )
    )
    await db_session.flush()
    return membership


async def _create_member_role(
    db_session: AsyncSession,
    tenant_id: uuid.UUID,
) -> Role:
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


async def test_admin_can_list_suspend_reactivate_and_revoke_managed_user_sessions(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin_ctx = await create_tenant_with_user(
        db_session,
        "identity-admin",
        role_code="admin",
        profile_type="admin",
    )
    member_ctx = await create_tenant_with_user(
        db_session,
        "identity-member",
        role_code="member",
        profile_type="member",
    )
    tenant_member_role = await _create_member_role(db_session, admin_ctx["tenant"].id)
    await _attach_existing_user_to_tenant(
        db_session,
        tenant_id=admin_ctx["tenant"].id,
        user=member_ctx["user"],
        role_id=tenant_member_role.id,
    )

    admin_token = await _login_access_token(
        client,
        email=admin_ctx["user"].email,
        password=admin_ctx["password"],
        tenant_slug=admin_ctx["tenant"].slug,
    )
    member_token = await _login_access_token(
        client,
        email=member_ctx["user"].email,
        password=member_ctx["password"],
        tenant_slug=admin_ctx["tenant"].slug,
    )
    session_id = decode_access_token(member_token)["sid"]
    refresh_token = create_refresh_token(member_ctx["user"].id, session_id=session_id)

    list_response = await client.get(
        f"/api/v1/auth/admin/managed-users/{admin_ctx['tenant'].id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert list_response.status_code == 200, list_response.text
    managed_user = next(
        row for row in list_response.json() if row["user_id"] == str(member_ctx["user"].id)
    )
    assert managed_user["membership_status"] == "active"

    revoke_response = await client.post(
        f"/api/v1/auth/admin/managed-users/{member_ctx['user'].id}/revoke-sessions",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert revoke_response.status_code == 200, revoke_response.text
    assert revoke_response.json()["revoked_session_count"] >= 1

    protected_after_revoke = await client.get(
        "/api/v1/auth/protected",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert protected_after_revoke.status_code == 401, protected_after_revoke.text

    refreshed_after_revoke = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refreshed_after_revoke.status_code == 401, refreshed_after_revoke.text

    member_token = await _login_access_token(
        client,
        email=member_ctx["user"].email,
        password=member_ctx["password"],
        tenant_slug=admin_ctx["tenant"].slug,
    )

    suspend_response = await client.post(
        f"/api/v1/auth/admin/managed-users/{member_ctx['user'].id}/suspend",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert suspend_response.status_code == 200, suspend_response.text
    assert suspend_response.json()["membership_status"] == "suspended"

    protected_after_suspend = await client.get(
        "/api/v1/auth/protected",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert protected_after_suspend.status_code == 401, protected_after_suspend.text

    suspended_login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": member_ctx["user"].email,
            "password": member_ctx["password"],
            "tenant_slug": admin_ctx["tenant"].slug,
        },
    )
    assert suspended_login.status_code == 403, suspended_login.text

    reactivate_response = await client.post(
        f"/api/v1/auth/admin/managed-users/{member_ctx['user'].id}/reactivate",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert reactivate_response.status_code == 200, reactivate_response.text
    assert reactivate_response.json()["membership_status"] == "active"

    restored_login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": member_ctx["user"].email,
            "password": member_ctx["password"],
            "tenant_slug": admin_ctx["tenant"].slug,
        },
    )
    assert restored_login.status_code == 200, restored_login.text


async def test_non_admin_cannot_manage_tenant_user_lifecycle(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin_ctx = await create_tenant_with_user(
        db_session,
        "identity-admin-2",
        role_code="admin",
        profile_type="admin",
    )
    member_ctx = await create_tenant_with_user(
        db_session,
        "identity-member-2",
        role_code="member",
        profile_type="member",
    )
    tenant_member_role = await _create_member_role(db_session, admin_ctx["tenant"].id)
    await _attach_existing_user_to_tenant(
        db_session,
        tenant_id=admin_ctx["tenant"].id,
        user=member_ctx["user"],
        role_id=tenant_member_role.id,
    )

    member_token = await _login_access_token(
        client,
        email=member_ctx["user"].email,
        password=member_ctx["password"],
        tenant_slug=admin_ctx["tenant"].slug,
    )

    list_response = await client.get(
        f"/api/v1/auth/admin/managed-users/{admin_ctx['tenant'].id}",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert list_response.status_code == 403, list_response.text

    suspend_response = await client.post(
        f"/api/v1/auth/admin/managed-users/{admin_ctx['user'].id}/suspend",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert suspend_response.status_code == 403, suspend_response.text


async def test_admin_cannot_manage_other_tenant_user_lifecycle(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    tenant_a = await create_tenant_with_user(
        db_session,
        "tenant-admin-a",
        role_code="admin",
        profile_type="admin",
    )
    tenant_b = await create_tenant_with_user(
        db_session,
        "tenant-admin-b",
        role_code="admin",
        profile_type="admin",
    )

    admin_token = await _login_access_token(
        client,
        email=tenant_a["user"].email,
        password=tenant_a["password"],
        tenant_slug=tenant_a["tenant"].slug,
    )

    suspend_response = await client.post(
        f"/api/v1/auth/admin/managed-users/{tenant_b['user'].id}/suspend",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert suspend_response.status_code == 404, suspend_response.text


async def test_admin_cannot_suspend_self(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
) -> None:
    data = seeded_tenant_and_admin
    admin_token = await _login_access_token(
        client,
        email=data["user"].email,
        password=data["password"],
        tenant_slug=data["tenant"].slug,
    )

    suspend_response = await client.post(
        f"/api/v1/auth/admin/managed-users/{data['user'].id}/suspend",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert suspend_response.status_code == 400, suspend_response.text
