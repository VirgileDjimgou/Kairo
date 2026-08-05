"""Integration coverage for assisted account recovery in a tenant context."""

from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.models import User
from app.modules.tenancy.models import TenantUser
from helpers import create_user_for_tenant, login


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role_code",
    ["president", "vice_president", "secretary_general", "principal_admin"],
)
async def test_authorized_office_roles_can_recover_member_access_without_data_loss(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
    db_session: AsyncSession,
    role_code: str,
) -> None:
    """Each authorized role can issue access, while the target keeps its membership."""
    tenant = seeded_tenant_and_admin["tenant"]
    officer = await create_user_for_tenant(
        db_session,
        tenant_id=tenant.id,
        email=f"{role_code}@test.org",
        password="OfficerPass123!",
        display_name=f"{role_code} Officer",
        role_code=role_code,
        profile_type="staff",
    )
    member = await create_user_for_tenant(
        db_session,
        tenant_id=tenant.id,
        email=f"member-{role_code}@test.org",
        password="MemberPass123!",
        display_name="Recoverable Member",
        role_code="member",
        profile_type="member",
        member_code=f"REC-{role_code[:4].upper()}",
    )
    officer_token = await login(client, officer["user"].email, officer["password"])
    old_member_token = await login(client, member["user"].email, member["password"])

    recovery = await client.post(
        f"/api/v1/auth/access-recovery/{member['user'].id}",
        json={"reason": "lost_access"},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert recovery.status_code == 200, recovery.text
    result = recovery.json()
    assert result["target_user_id"] == str(member["user"].id)
    assert result["target_display_name"] == "Recoverable Member"
    assert result["temporary_password"].startswith("Kairo-")
    assert result["expires_at"]

    old_session = await client.get(
        "/api/v1/auth/protected",
        headers={"Authorization": f"Bearer {old_member_token}"},
    )
    assert old_session.status_code == 401

    old_password_login = await client.post(
        "/api/v1/auth/login",
        json={"email": member["user"].email, "password": member["password"]},
    )
    assert old_password_login.status_code == 401

    temporary_login = await client.post(
        "/api/v1/auth/login",
        json={"email": member["user"].email, "password": result["temporary_password"]},
    )
    assert temporary_login.status_code == 200, temporary_login.text
    assert temporary_login.json()["password_change_required"] is True

    change = await client.post(
        "/api/v1/auth/change-initial-password",
        json={"new_password": "MemberReplacement123!"},
        headers={"Authorization": f"Bearer {temporary_login.json()['access_token']}"},
    )
    assert change.status_code == 200, change.text

    final_login = await client.post(
        "/api/v1/auth/login",
        json={"email": member["user"].email, "password": "MemberReplacement123!"},
    )
    assert final_login.status_code == 200, final_login.text
    assert final_login.json()["password_change_required"] is False

    persisted_user = await db_session.scalar(select(User).where(User.id == member["user"].id))
    persisted_membership = await db_session.scalar(
        select(TenantUser).where(
            TenantUser.tenant_id == tenant.id,
            TenantUser.user_id == member["user"].id,
        )
    )
    assert persisted_user is not None
    assert persisted_user.display_name == "Recoverable Member"
    assert persisted_user.temporary_password_expires_at is None
    assert persisted_membership is not None
    assert persisted_membership.membership_status == "active"


@pytest.mark.asyncio
async def test_recovery_rejects_roles_without_recovery_authority(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
    db_session: AsyncSession,
) -> None:
    tenant = seeded_tenant_and_admin["tenant"]
    treasurer = await create_user_for_tenant(
        db_session,
        tenant_id=tenant.id,
        email="treasurer@test.org",
        password="TreasurerPass123!",
        display_name="Treasurer",
        role_code="treasurer",
        profile_type="staff",
    )
    member = await create_user_for_tenant(
        db_session,
        tenant_id=tenant.id,
        email="member@test.org",
        password="MemberPass123!",
        display_name="Member",
    )
    token = await login(client, treasurer["user"].email, treasurer["password"])

    response = await client.post(
        f"/api/v1/auth/access-recovery/{member['user'].id}",
        json={"reason": "forgotten_password"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_member_can_change_own_password_without_email_or_membership_loss(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
    db_session: AsyncSession,
) -> None:
    tenant = seeded_tenant_and_admin["tenant"]
    member = await create_user_for_tenant(
        db_session,
        tenant_id=tenant.id,
        email="self-service-member@combis.org",
        password="MemberPass123!",
        display_name="Self Service Member",
    )
    token = await login(client, member["user"].email, member["password"])

    response = await client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": member["password"],
            "new_password": "SelfServiceReplacement123!",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text

    old_login = await client.post(
        "/api/v1/auth/login",
        json={"email": member["user"].email, "password": member["password"]},
    )
    assert old_login.status_code == 401
    new_login = await client.post(
        "/api/v1/auth/login",
        json={"email": member["user"].email, "password": "SelfServiceReplacement123!"},
    )
    assert new_login.status_code == 200, new_login.text

    membership = await db_session.scalar(
        select(TenantUser).where(
            TenantUser.tenant_id == tenant.id,
            TenantUser.user_id == member["user"].id,
        )
    )
    assert membership is not None
    assert membership.membership_status == "active"


@pytest.mark.asyncio
async def test_expired_temporary_access_is_rejected(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
    db_session: AsyncSession,
) -> None:
    tenant = seeded_tenant_and_admin["tenant"]
    officer = await create_user_for_tenant(
        db_session,
        tenant_id=tenant.id,
        email="president-expiry@test.org",
        password="OfficerPass123!",
        display_name="President",
        role_code="president",
        profile_type="staff",
    )
    member = await create_user_for_tenant(
        db_session,
        tenant_id=tenant.id,
        email="expired-member@test.org",
        password="MemberPass123!",
        display_name="Member",
    )
    officer_token = await login(client, officer["user"].email, officer["password"])
    recovery = await client.post(
        f"/api/v1/auth/access-recovery/{member['user'].id}",
        json={"reason": "security_reset"},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert recovery.status_code == 200, recovery.text

    user = await db_session.scalar(select(User).where(User.id == member["user"].id))
    assert user is not None
    user.temporary_password_expires_at = datetime.now(UTC) - timedelta(minutes=1)
    await db_session.flush()

    expired_login = await client.post(
        "/api/v1/auth/login",
        json={"email": member["user"].email, "password": recovery.json()["temporary_password"]},
    )
    assert expired_login.status_code == 403
    assert "expired" in expired_login.json()["detail"].lower()
