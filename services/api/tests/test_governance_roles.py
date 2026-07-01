import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.capabilities import CAP_ROLE_ASSIGN, CAP_TENANT_SETTINGS_WRITE
from app.core.dependencies import CurrentUser
from helpers import create_tenant_with_user, create_user_for_tenant, login


@pytest.mark.asyncio
async def test_admin_can_list_tenant_roles_with_canonical_governance_catalog(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
) -> None:
    data = seeded_tenant_and_admin
    token = await login(
        client,
        data["user"].email,
        data["password"],
        tenant_slug=data["tenant"].slug,
    )

    response = await client.get(
        f"/api/v1/tenants/{data['tenant'].id}/roles",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    codes = {item["code"] for item in body}
    assert {
        "principal_admin",
        "president",
        "vice_president",
        "secretary_general",
        "treasurer",
        "auditor",
        "censor",
        "sports_manager",
        "member",
    }.issubset(codes)
    secretary_role = next(item for item in body if item["code"] == "secretary_general")
    assert secretary_role["is_canonical"] is True
    assert "documents:write" in secretary_role["capabilities"]


@pytest.mark.asyncio
async def test_admin_can_update_managed_user_roles_and_audit_change(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin_ctx = await create_tenant_with_user(
        db_session,
        "gov-admin",
        role_code="admin",
        profile_type="admin",
    )
    member_ctx = await create_user_for_tenant(
        db_session,
        tenant_id=admin_ctx["tenant"].id,
        email="managed-user@test.org",
        password="ManagedPass123!",
        display_name="Managed User",
        role_code="member",
        profile_type="member",
    )
    admin_token = await login(
        client,
        admin_ctx["user"].email,
        admin_ctx["password"],
        tenant_slug=admin_ctx["tenant"].slug,
    )

    response = await client.put(
        f"/api/v1/auth/admin/managed-users/{member_ctx['user'].id}/roles",
        json={"role_codes": ["member", "secretary_general"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200, response.text
    assert sorted(response.json()["role_codes"]) == ["member", "secretary_general"]

    managed_users = await client.get(
        f"/api/v1/auth/admin/managed-users/{admin_ctx['tenant'].id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert managed_users.status_code == 200, managed_users.text
    managed_row = next(
        item for item in managed_users.json() if item["user_id"] == str(member_ctx["user"].id)
    )
    assert managed_row["roles"] == ["member", "secretary_general"]

    audit_response = await client.get(
        "/api/v1/admin/audit/events",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"entity_type": "tenant_user"},
    )
    assert audit_response.status_code == 200, audit_response.text
    audit_event = next(
        item
        for item in audit_response.json()
        if item["action"] == "roles_updated"
        and item["details"]["target_user_id"] == str(member_ctx["user"].id)
    )
    assert audit_event["details"]["added_role_codes"] == ["secretary_general"]


@pytest.mark.asyncio
async def test_accept_invite_records_role_assignment_audit_for_canonical_role(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
) -> None:
    data = seeded_tenant_and_admin
    admin_token = await login(
        client,
        data["user"].email,
        data["password"],
        tenant_slug=data["tenant"].slug,
    )

    invite_response = await client.post(
        "/api/v1/auth/invite",
        json={
            "email": "secretary.invited@test.org",
            "role_code": "secretary_general",
            "tenant_id": str(data["tenant"].id),
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert invite_response.status_code == 201, invite_response.text
    invite_token = invite_response.json()["invite_token"]
    assert invite_token is not None

    accept_response = await client.post(
        "/api/v1/auth/accept-invite",
        json={
            "token": invite_token,
            "display_name": "Secretary Invitee",
            "password": "Secretary123!",
        },
    )
    assert accept_response.status_code == 200, accept_response.text

    audit_response = await client.get(
        "/api/v1/admin/audit/events",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"entity_type": "tenant_user"},
    )
    assert audit_response.status_code == 200, audit_response.text
    role_event = next(
        item
        for item in audit_response.json()
        if item["action"] == "role_assigned"
        and item["details"]["role_code"] == "secretary_general"
    )
    assert role_event["details"]["source"] == "invitation_acceptance"


def test_current_user_capability_checks_support_legacy_and_canonical_roles() -> None:
    fake_user = object()
    fake_uuid = uuid.uuid4()
    current_admin = CurrentUser(
        user=fake_user,
        tenant_id=fake_uuid,
        roles=["admin"],
        session_id=fake_uuid,
    )
    current_principal = CurrentUser(
        user=fake_user,
        tenant_id=fake_uuid,
        roles=["principal_admin"],
        session_id=fake_uuid,
    )

    assert current_admin.has_capability(CAP_ROLE_ASSIGN)
    assert current_admin.has_capability(CAP_TENANT_SETTINGS_WRITE)
    assert current_principal.has_capability(CAP_ROLE_ASSIGN)
