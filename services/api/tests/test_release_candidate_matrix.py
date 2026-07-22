from __future__ import annotations

import uuid as _uuid
from dataclasses import dataclass

import pytest
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


@dataclass(frozen=True)
class MatrixCase:
    role_code: str
    display_name: str
    email_prefix: str
    password: str
    profile_type: str
    member_code: str
    allowed_method: str
    allowed_path: str
    allowed_json: dict | None = None
    allowed_params: dict | None = None
    expected_allowed_status: int = 200
    denied_method: str | None = None
    denied_path: str | None = None
    denied_json: dict | None = None
    denied_params: dict | None = None
    expected_denied_status: int = 403


async def _create_profile(
    client: AsyncClient,
    token: str,
    *,
    member_code: str,
    first_name: str,
    last_name: str,
    display_name: str,
    email: str,
) -> dict:
    response = await client.post(
        "/api/v1/memberships/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "member_code": member_code,
            "first_name": first_name,
            "last_name": last_name,
            "display_name": display_name,
            "email": email,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _create_contribution(
    client: AsyncClient,
    token: str,
    *,
    membership_profile_id: str,
    year: int = 2026,
) -> dict:
    response = await client.post(
        "/api/v1/contributions/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "membership_profile_id": membership_profile_id,
            "year": year,
            "expected_amount": "120.00",
            "paid_amount": "45.00",
            "currency": "EUR",
            "status": "partial",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _create_policy(client: AsyncClient, token: str) -> dict:
    response = await client.post(
        "/api/v1/policies/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Release Candidate Policy",
            "category": "governance",
            "description": "Matrix seed policy for release verification.",
            "status": "published",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _create_disciplinary_record(
    client: AsyncClient,
    token: str,
    *,
    membership_profile_id: str,
    policy_record_id: str,
) -> dict:
    response = await client.post(
        "/api/v1/disciplinary/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "membership_profile_id": membership_profile_id,
            "policy_record_id": policy_record_id,
            "title": "Release candidate review",
            "description": "Temporary record for matrix coverage.",
            "amount": "10.00",
            "currency": "EUR",
            "status": "under_review",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _request(
    client: AsyncClient,
    token: str,
    *,
    method: str,
    path: str,
    json: dict | None = None,
    params: dict | None = None,
) -> object:
    return await client.request(
        method,
        path,
        headers={"Authorization": f"Bearer {token}"},
        json=json,
        params=params,
    )


MATRIX_CASES = (
    MatrixCase(
        role_code="member",
        display_name="Member User",
        email_prefix="member",
        password="MemberPass1!",
        profile_type="member",
        member_code="MEM-001",
        allowed_method="GET",
        allowed_path="/api/v1/memberships/me/statement",
        denied_method="GET",
        denied_path="/api/v1/memberships/",
    ),
    MatrixCase(
        role_code="secretary_general",
        display_name="Secretary General",
        email_prefix="secretary",
        password="SecretaryPass1!",
        profile_type="staff",
        member_code="SEC-001",
        allowed_method="POST",
        allowed_path="/api/v1/policies/",
        allowed_json={
            "title": "Secretary Release Checklist",
            "category": "governance",
            "description": "Official records and publication control.",
            "status": "draft",
        },
        expected_allowed_status=201,
        denied_method="POST",
        denied_path="/api/v1/contributions/",
        denied_json={
            "membership_profile_id": "{member_profile_id}",
            "year": 2027,
            "expected_amount": "25.00",
            "paid_amount": "0.00",
            "currency": "EUR",
            "status": "pending",
        },
    ),
    MatrixCase(
        role_code="treasurer",
        display_name="Treasurer User",
        email_prefix="treasurer",
        password="TreasurerPass1!",
        profile_type="staff",
        member_code="TRE-001",
        allowed_method="POST",
        allowed_path="/api/v1/contributions/",
        allowed_json={
            "membership_profile_id": "{member_profile_id}",
            "year": 2027,
            "expected_amount": "50.00",
            "paid_amount": "10.00",
            "currency": "EUR",
            "status": "partial",
        },
        expected_allowed_status=201,
        denied_method="POST",
        denied_path="/api/v1/disciplinary/",
        denied_json={
            "membership_profile_id": "{member_profile_id}",
            "title": "Should be blocked",
            "description": "Treasurer must not create sanctions.",
            "status": "open",
            "severity": "low",
        },
    ),
    MatrixCase(
        role_code="auditor",
        display_name="Auditor User",
        email_prefix="auditor",
        password="AuditorPass1!",
        profile_type="staff",
        member_code="AUD-001",
        allowed_method="GET",
        allowed_path="/api/v1/admin/audit/events",
        denied_method="POST",
        denied_path="/api/v1/contributions/",
        denied_json={
            "membership_profile_id": "{member_profile_id}",
            "year": 2027,
            "expected_amount": "50.00",
            "paid_amount": "0.00",
            "currency": "EUR",
            "status": "pending",
        },
    ),
    MatrixCase(
        role_code="censor",
        display_name="Censor User",
        email_prefix="censor",
        password="CensorPass1!",
        profile_type="staff",
        member_code="CEN-001",
        allowed_method="POST",
        allowed_path="/api/v1/disciplinary/",
        allowed_json={
            "membership_profile_id": "{member_profile_id}",
            "policy_record_id": "{policy_record_id}",
            "title": "Release candidate review",
            "description": "Disciplinary placeholder for the matrix.",
            "amount": "10.00",
            "currency": "EUR",
            "status": "under_review",
        },
        expected_allowed_status=201,
        denied_method="POST",
        denied_path="/api/v1/contributions/",
        denied_json={
            "membership_profile_id": "{member_profile_id}",
            "year": 2027,
            "expected_amount": "50.00",
            "paid_amount": "0.00",
            "currency": "EUR",
            "status": "pending",
        },
    ),
    MatrixCase(
        role_code="sports_manager",
        display_name="Sports Manager",
        email_prefix="sports",
        password="SportsPass1!",
        profile_type="staff",
        member_code="SPT-001",
        allowed_method="POST",
        allowed_path="/api/v1/sports/events",
        allowed_json={
            "title": "Release Candidate Scrimmage",
            "start_at": "2026-08-10T09:00:00Z",
            "end_at": "2026-08-10T11:00:00Z",
            "visibility_scope": "members_only",
            "status": "published",
            "metadata_json": {"sport_type": "training"},
        },
        expected_allowed_status=201,
        denied_method="POST",
        denied_path="/api/v1/announcements/",
        denied_json={
            "title": "Unauthorized notice",
            "body": "Sports manager must not publish announcements.",
            "visibility_scope": "tenant_public",
        },
    ),
    MatrixCase(
        role_code="president",
        display_name="President User",
        email_prefix="president",
        password="PresidentPass1!",
        profile_type="staff",
        member_code="PRE-001",
        allowed_method="GET",
        allowed_path="/api/v1/admin/audit/events",
        allowed_params={"limit": 5},
        denied_method="PUT",
        denied_path="/api/v1/tenants/{tenant_id}/settings",
        denied_json={"name": "Blocked president settings"},
    ),
    MatrixCase(
        role_code="vice_president",
        display_name="Vice President User",
        email_prefix="vice-president",
        password="VicePresidentPass1!",
        profile_type="staff",
        member_code="VPR-001",
        allowed_method="GET",
        allowed_path="/api/v1/contributions/summary",
        allowed_params={"year": 2026},
        denied_method="GET",
        denied_path="/api/v1/admin/audit/events",
        denied_params={"limit": 5},
    ),
    MatrixCase(
        role_code="principal_admin",
        display_name="Principal Admin User",
        email_prefix="principal",
        password="PrincipalPass1!",
        profile_type="admin",
        member_code="PAD-001",
        allowed_method="PUT",
        allowed_path="/api/v1/tenants/{tenant_id}/settings",
        allowed_json={"name": "Principal Release Org"},
        denied_method="PUT",
        denied_path="/api/v1/tenants/{other_tenant_id}/settings",
        denied_json={"name": "Cross-tenant block"},
    ),
)


async def _login_role(
    client: AsyncClient,
    *,
    email: str,
    password: str,
    tenant_slug: str,
) -> str:
    return await login(client, email, password, tenant_slug=tenant_slug)


@pytest.mark.asyncio
async def test_release_candidate_role_matrix(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    tenant_ctx = await create_tenant_with_user(
        db_session,
        f"rc-{_uuid.uuid4().hex[:6]}",
    )
    admin_token = await _login_role(
        client,
        email=tenant_ctx["user"].email,
        password=tenant_ctx["password"],
        tenant_slug=tenant_ctx["tenant"].slug,
    )

    role_users: dict[str, dict] = {}
    for case in MATRIX_CASES:
        role_users[case.role_code] = await create_user_for_tenant(
            db_session,
            tenant_id=tenant_ctx["tenant"].id,
            email=f"{case.email_prefix}-{_uuid.uuid4().hex[:6]}@test.org",
            password=case.password,
            display_name=case.display_name,
            role_code=case.role_code,
            profile_type=case.profile_type,
            member_code=case.member_code,
        )

    other_tenant_ctx = await create_tenant_with_user(
        db_session,
        f"rc-other-{_uuid.uuid4().hex[:6]}",
    )
    await db_session.commit()

    member_profile = role_users["member"]["profile"]
    assert member_profile is not None

    await _create_contribution(
        client,
        admin_token,
        membership_profile_id=str(member_profile.id),
    )
    policy = await _create_policy(client, admin_token)
    await _create_disciplinary_record(
        client,
        admin_token,
        membership_profile_id=str(member_profile.id),
        policy_record_id=policy["id"],
    )

    for case in MATRIX_CASES:
        user_ctx = role_users[case.role_code]
        token = await _login_role(
            client,
            email=user_ctx["user"].email,
            password=user_ctx["password"],
            tenant_slug=tenant_ctx["tenant"].slug,
        )

        allowed_json = None
        if case.allowed_json is not None:
            allowed_json = {
                key: (
                    str(member_profile.id)
                    if value == "{member_profile_id}"
                    else policy["id"]
                    if value == "{policy_record_id}"
                    else str(tenant_ctx["tenant"].id)
                    if value == "{tenant_id}"
                    else value
                )
                for key, value in case.allowed_json.items()
            }

        allowed_response = await _request(
            client,
            token,
            method=case.allowed_method,
            path=case.allowed_path.format(tenant_id=tenant_ctx["tenant"].id),
            json=allowed_json,
            params=case.allowed_params,
        )
        assert allowed_response.status_code == case.expected_allowed_status, (
            case.role_code,
            allowed_response.text,
        )

        if case.denied_path is None or case.denied_method is None:
            continue

        denied_json = None
        if case.denied_json is not None:
            denied_json = {
                key: (
                    str(member_profile.id)
                    if value == "{member_profile_id}"
                    else policy["id"]
                    if value == "{policy_record_id}"
                    else str(tenant_ctx["tenant"].id)
                    if value == "{tenant_id}"
                    else str(other_tenant_ctx["tenant"].id)
                    if value == "{other_tenant_id}"
                    else value
                )
                for key, value in case.denied_json.items()
            }

        denied_response = await _request(
            client,
            token,
            method=case.denied_method,
            path=case.denied_path.format(
                tenant_id=tenant_ctx["tenant"].id,
                other_tenant_id=other_tenant_ctx["tenant"].id,
            ),
            json=denied_json,
            params=case.denied_params,
        )
        assert denied_response.status_code == case.expected_denied_status, (
            case.role_code,
            denied_response.text,
        )


@pytest.mark.asyncio
async def test_principal_admin_cannot_update_other_tenant_settings(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    tenant_ctx = await create_tenant_with_user(
        db_session,
        f"rc-pa-{_uuid.uuid4().hex[:6]}",
    )
    principal_admin = await create_user_for_tenant(
        db_session,
        tenant_id=tenant_ctx["tenant"].id,
        email=f"principal-admin-{_uuid.uuid4().hex[:6]}@test.org",
        password="PrincipalPass2!",
        display_name="Principal Admin",
        role_code="principal_admin",
        profile_type="admin",
        member_code="PA-001",
    )
    other_tenant_ctx = await create_tenant_with_user(
        db_session,
        f"rc-pa-other-{_uuid.uuid4().hex[:6]}",
    )
    await db_session.commit()

    token = await _login_role(
        client,
        email=principal_admin["user"].email,
        password=principal_admin["password"],
        tenant_slug=tenant_ctx["tenant"].slug,
    )

    allowed = await _request(
        client,
        token,
        method="PUT",
        path=f"/api/v1/tenants/{tenant_ctx['tenant'].id}/settings",
        json={"name": "Principal RC Org"},
    )
    assert allowed.status_code == 200, allowed.text

    denied = await _request(
        client,
        token,
        method="PUT",
        path=f"/api/v1/tenants/{other_tenant_ctx['tenant'].id}/settings",
        json={"name": "Cross Tenant Block"},
    )
    assert denied.status_code == 403, denied.text
