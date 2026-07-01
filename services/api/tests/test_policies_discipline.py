"""Sprint 9 integration tests: policies and disciplinary records."""

from __future__ import annotations

import uuid as _uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.identity.models import User
from app.modules.membership.models import MembershipProfile
from app.modules.tenancy.models import Role, TenantUser, user_roles
from helpers import create_tenant_with_user, login


async def _create_linked_member(
    db: AsyncSession,
    *,
    tenant_id,
    email: str,
    password: str,
    member_code: str,
    display_name: str,
    role_code: str = "member",
) -> dict:
    user = User(
        id=_uuid.uuid4(),
        email=email,
        password_hash=hash_password(password),
        display_name=display_name,
        status="active",
    )
    db.add(user)
    await db.flush()

    role = await db.scalar(
        select(Role).where(
            Role.tenant_id == tenant_id,
            Role.code == role_code,
        )
    )
    if role is None:
        role = Role(
            id=_uuid.uuid4(),
            tenant_id=tenant_id,
            code=role_code,
            name=role_code.title(),
            is_system_role=role_code in {"admin", "member"},
        )
        db.add(role)
        await db.flush()

    tenant_user = TenantUser(
        id=_uuid.uuid4(),
        tenant_id=tenant_id,
        user_id=user.id,
        profile_type=role_code,
        membership_status="active",
    )
    db.add(tenant_user)
    await db.flush()

    await db.execute(
        user_roles.insert().values(
            tenant_user_id=tenant_user.id,
            role_id=role.id,
        )
    )

    profile = MembershipProfile(
        id=_uuid.uuid4(),
        tenant_id=tenant_id,
        user_id=user.id,
        member_code=member_code,
        first_name=display_name.split()[0],
        last_name=display_name.split()[-1],
        display_name=display_name,
        email=email,
        status="active",
    )
    db.add(profile)
    await db.flush()
    return {"user": user, "password": password, "profile": profile, "tenant_user": tenant_user, "role": role}


@pytest.mark.asyncio
async def test_admin_can_create_public_policies_and_users_can_read_them(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"policy-{_uuid.uuid4().hex[:6]}")
    member = await _create_linked_member(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"member-{_uuid.uuid4().hex[:6]}@test.org",
        password="MemberPass1!",
        member_code="M-100",
        display_name="Member One",
    )

    admin_token = await login(client, admin["user"].email, admin["password"], tenant_slug=admin["tenant"].slug)
    member_token = await login(client, member["user"].email, member["password"], tenant_slug=admin["tenant"].slug)

    created = await client.post(
        "/api/v1/policies/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Code of Conduct",
            "category": "conduct",
            "description": "Respect the association rules.",
            "status": "published",
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["title"] == "Code of Conduct"
    assert body["status"] == "published"

    public_list = await client.get(
        "/api/v1/policies/public",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert public_list.status_code == 200, public_list.text
    policies = public_list.json()
    assert len(policies) == 1
    assert policies[0]["title"] == "Code of Conduct"

    categories = await client.get(
        "/api/v1/policies/categories",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert categories.status_code == 200
    assert categories.json()["categories"] == ["conduct"]


@pytest.mark.asyncio
async def test_non_admin_cannot_manage_policies(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"policy-lock-{_uuid.uuid4().hex[:6]}")
    member = await _create_linked_member(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"member-lock-{_uuid.uuid4().hex[:6]}@test.org",
        password="MemberPass2!",
        member_code="M-200",
        display_name="Member Two",
    )
    member_token = await login(client, member["user"].email, member["password"], tenant_slug=admin["tenant"].slug)

    response = await client.post(
        "/api/v1/policies/",
        headers={"Authorization": f"Bearer {member_token}"},
        json={"title": "Blocked Policy", "category": "conduct"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_member_cannot_see_other_members_disciplinary_record(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"disc-{_uuid.uuid4().hex[:6]}")
    subject = await _create_linked_member(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"subject-{_uuid.uuid4().hex[:6]}@test.org",
        password="SubjectPass1!",
        member_code="S-001",
        display_name="Subject Member",
    )
    viewer = await _create_linked_member(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"viewer-{_uuid.uuid4().hex[:6]}@test.org",
        password="ViewerPass1!",
        member_code="V-001",
        display_name="Viewer Member",
    )

    admin_token = await login(client, admin["user"].email, admin["password"], tenant_slug=admin["tenant"].slug)
    subject_token = await login(client, subject["user"].email, subject["password"], tenant_slug=admin["tenant"].slug)
    viewer_token = await login(client, viewer["user"].email, viewer["password"], tenant_slug=admin["tenant"].slug)

    policy_resp = await client.post(
        "/api/v1/policies/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Attendance Rule", "category": "attendance", "status": "published"},
    )
    assert policy_resp.status_code == 201, policy_resp.text
    policy_id = policy_resp.json()["id"]

    disciplinary_resp = await client.post(
        "/api/v1/disciplinary/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "membership_profile_id": str(subject["profile"].id),
            "policy_record_id": policy_id,
            "title": "Late arrival warning",
            "description": "Repeated late arrivals to meetings.",
            "amount": "25.00",
            "currency": "EUR",
            "status": "open",
        },
    )
    assert disciplinary_resp.status_code == 201, disciplinary_resp.text
    disciplinary_id = disciplinary_resp.json()["id"]

    my_records = await client.get(
        "/api/v1/disciplinary/me",
        headers={"Authorization": f"Bearer {subject_token}"},
    )
    assert my_records.status_code == 200, my_records.text
    assert len(my_records.json()) == 1
    assert my_records.json()[0]["title"] == "Late arrival warning"

    viewer_attempt = await client.get(
        f"/api/v1/disciplinary/{disciplinary_id}",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert viewer_attempt.status_code == 404

    staff_list = await client.get(
        "/api/v1/disciplinary/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert staff_list.status_code == 200
    assert len(staff_list.json()) == 1


@pytest.mark.asyncio
async def test_admin_can_get_policy_by_id(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"policy-get-{_uuid.uuid4().hex[:6]}")
    admin_token = await login(client, admin["user"].email, admin["password"], tenant_slug=admin["tenant"].slug)

    created = await client.post(
        "/api/v1/policies/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Data Policy", "category": "data", "description": "Data handling rules.", "status": "published"},
    )
    assert created.status_code == 201
    policy_id = created.json()["id"]

    get_resp = await client.get(
        f"/api/v1/policies/{policy_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Data Policy"


@pytest.mark.asyncio
async def test_admin_can_list_all_policies(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"policy-list-{_uuid.uuid4().hex[:6]}")
    admin_token = await login(client, admin["user"].email, admin["password"], tenant_slug=admin["tenant"].slug)

    for title in ["Policy A", "Policy B"]:
        await client.post(
            "/api/v1/policies/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"title": title, "category": "general", "status": "published"},
        )

    list_resp = await client.get(
        "/api/v1/policies/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 2


@pytest.mark.asyncio
async def test_admin_can_update_policy(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"policy-upd-{_uuid.uuid4().hex[:6]}")
    admin_token = await login(client, admin["user"].email, admin["password"], tenant_slug=admin["tenant"].slug)

    created = await client.post(
        "/api/v1/policies/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Old Title", "category": "general", "status": "draft"},
    )
    policy_id = created.json()["id"]

    patch_resp = await client.patch(
        f"/api/v1/policies/{policy_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "New Title", "status": "published"},
    )
    assert patch_resp.status_code == 200, patch_resp.text
    updated = patch_resp.json()
    assert updated["title"] == "New Title"
    assert updated["status"] == "published"


@pytest.mark.asyncio
async def test_admin_can_delete_policy(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"policy-del-{_uuid.uuid4().hex[:6]}")
    admin_token = await login(client, admin["user"].email, admin["password"], tenant_slug=admin["tenant"].slug)

    created = await client.post(
        "/api/v1/policies/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Delete Me", "category": "general", "status": "published"},
    )
    policy_id = created.json()["id"]

    delete_resp = await client.delete(
        f"/api/v1/policies/{policy_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert delete_resp.status_code == 204

    get_resp = await client.get(
        f"/api/v1/policies/{policy_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_admin_can_update_disciplinary_record(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"disc-upd-{_uuid.uuid4().hex[:6]}")
    subject = await _create_linked_member(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"disc-subj-{_uuid.uuid4().hex[:6]}@test.org",
        password="DiscSubj1!",
        member_code="DS-001",
        display_name="Disc Subject",
    )
    admin_token = await login(client, admin["user"].email, admin["password"], tenant_slug=admin["tenant"].slug)

    created = await client.post(
        "/api/v1/disciplinary/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "membership_profile_id": str(subject["profile"].id),
            "title": "Initial warning",
            "amount": "50.00",
            "currency": "EUR",
            "status": "open",
        },
    )
    assert created.status_code == 201
    record_id = created.json()["id"]

    patch_resp = await client.patch(
        f"/api/v1/disciplinary/{record_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "resolved", "amount": "25.00"},
    )
    assert patch_resp.status_code == 200, patch_resp.text
    updated = patch_resp.json()
    assert updated["status"] == "resolved"
    assert updated["amount"] == "25.00"


@pytest.mark.asyncio
async def test_admin_can_delete_disciplinary_record(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"disc-del-{_uuid.uuid4().hex[:6]}")
    subject = await _create_linked_member(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"disc-subj2-{_uuid.uuid4().hex[:6]}@test.org",
        password="DiscSubj2!",
        member_code="DS-002",
        display_name="Disc Subject Two",
    )
    admin_token = await login(client, admin["user"].email, admin["password"], tenant_slug=admin["tenant"].slug)

    created = await client.post(
        "/api/v1/disciplinary/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "membership_profile_id": str(subject["profile"].id),
            "title": "Temp record",
            "amount": "10.00",
            "currency": "EUR",
            "status": "open",
        },
    )
    assert created.status_code == 201
    record_id = created.json()["id"]

    delete_resp = await client.delete(
        f"/api/v1/disciplinary/{record_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert delete_resp.status_code == 204

    get_resp = await client.get(
        f"/api/v1/disciplinary/{record_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_treasurer_cannot_create_disciplinary_record(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"treasurer-{_uuid.uuid4().hex[:6]}")
    treasurer = await _create_linked_member(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"treasurer-{_uuid.uuid4().hex[:6]}@test.org",
        password="TreasurerPass1!",
        member_code="T-001",
        display_name="Treasurer Member",
        role_code="treasurer",
    )
    subject = await _create_linked_member(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"subject2-{_uuid.uuid4().hex[:6]}@test.org",
        password="Subject2Pass1!",
        member_code="S-002",
        display_name="Subject Two",
    )

    admin_token = await login(client, admin["user"].email, admin["password"], tenant_slug=admin["tenant"].slug)
    treasurer_token = await login(client, treasurer["user"].email, treasurer["password"], tenant_slug=admin["tenant"].slug)

    policy_resp = await client.post(
        "/api/v1/policies/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Meeting Rule", "category": "conduct", "status": "published"},
    )
    policy_id = policy_resp.json()["id"]

    response = await client.post(
        "/api/v1/disciplinary/",
        headers={"Authorization": f"Bearer {treasurer_token}"},
        json={
            "membership_profile_id": str(subject["profile"].id),
            "policy_record_id": policy_id,
            "title": "Code reminder",
            "amount": "10.00",
            "currency": "EUR",
            "status": "under_review",
        },
    )
    assert response.status_code == 403, response.text
