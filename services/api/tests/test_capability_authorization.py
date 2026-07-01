from __future__ import annotations

import uuid as _uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from helpers import create_tenant_with_user, create_user_for_tenant, login


pytestmark = pytest.mark.asyncio


async def _create_profile(
    client: AsyncClient,
    token: str,
    *,
    member_code: str,
    display_name: str,
    email: str,
) -> dict:
    response = await client.post(
        "/api/v1/memberships/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "member_code": member_code,
            "first_name": display_name.split()[0],
            "last_name": display_name.split()[-1],
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
) -> dict:
    response = await client.post(
        "/api/v1/contributions/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "membership_profile_id": membership_profile_id,
            "year": 2026,
            "expected_amount": "120.00",
            "paid_amount": "20.00",
            "currency": "EUR",
            "status": "partial",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_secretary_general_can_manage_documents_policies_and_announcements(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"sec-admin-{_uuid.uuid4().hex[:6]}")
    secretary = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"secretary-{_uuid.uuid4().hex[:6]}@test.org",
        password="SecretaryPass1!",
        display_name="Secretary General",
        role_code="secretary_general",
        profile_type="staff",
    )
    await db_session.commit()

    secretary_token = await login(
        client,
        secretary["user"].email,
        secretary["password"],
        admin["tenant"].slug,
    )

    upload = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {secretary_token}"},
        files={"file": ("minutes.txt", b"official meeting minutes", "text/plain")},
        data={"title": "Meeting Minutes", "access_scope": "tenant_public"},
    )
    assert upload.status_code == 200, upload.text

    policy = await client.post(
        "/api/v1/policies/",
        headers={"Authorization": f"Bearer {secretary_token}"},
        json={
            "title": "Records Policy",
            "category": "governance",
            "description": "Official records management.",
            "status": "draft",
        },
    )
    assert policy.status_code == 201, policy.text

    announcement = await client.post(
        "/api/v1/announcements/",
        headers={"Authorization": f"Bearer {secretary_token}"},
        json={
            "title": "Board Notice",
            "body": "Next board meeting on Friday.",
            "visibility_scope": "members_only",
            "status": "published",
            "published_at": "2026-07-01T00:00:00Z",
        },
    )
    assert announcement.status_code == 201, announcement.text

    profile = await _create_profile(
        client,
        await login(client, admin["user"].email, admin["password"], admin["tenant"].slug),
        member_code="SEC-001",
        display_name="Secretary Protected",
        email="secretary-protected@test.org",
    )

    finance_mutation = await client.post(
        "/api/v1/contributions/",
        headers={"Authorization": f"Bearer {secretary_token}"},
        json={
            "membership_profile_id": profile["id"],
            "year": 2026,
            "expected_amount": "25.00",
            "paid_amount": "0.00",
            "currency": "EUR",
            "status": "pending",
        },
    )
    assert finance_mutation.status_code == 403, finance_mutation.text

    disciplinary_mutation = await client.post(
        "/api/v1/disciplinary/",
        headers={"Authorization": f"Bearer {secretary_token}"},
        json={
            "membership_profile_id": profile["id"],
            "title": "Unauthorized sanction",
            "description": "Should be blocked",
            "status": "open",
            "severity": "low",
        },
    )
    assert disciplinary_mutation.status_code == 403, disciplinary_mutation.text


async def test_sports_manager_can_manage_events_but_not_announcements(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"sport-admin-{_uuid.uuid4().hex[:6]}")
    manager = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"sports-{_uuid.uuid4().hex[:6]}@test.org",
        password="SportsPass1!",
        display_name="Sports Manager",
        role_code="sports_manager",
        profile_type="staff",
    )
    await db_session.commit()

    manager_token = await login(
        client,
        manager["user"].email,
        manager["password"],
        admin["tenant"].slug,
    )

    event = await client.post(
        "/api/v1/events/",
        headers={"Authorization": f"Bearer {manager_token}"},
        json={
            "title": "Interclub Tournament",
            "start_at": "2026-08-10T09:00:00Z",
            "end_at": "2026-08-10T18:00:00Z",
            "visibility_scope": "members_only",
            "status": "published",
        },
    )
    assert event.status_code == 201, event.text

    announcement = await client.post(
        "/api/v1/announcements/",
        headers={"Authorization": f"Bearer {manager_token}"},
        json={
            "title": "Unauthorized Notice",
            "body": "Should fail",
            "visibility_scope": "tenant_public",
        },
    )
    assert announcement.status_code == 403, announcement.text


async def test_auditor_can_read_finance_and_audit_but_cannot_mutate_finance(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"aud-admin-{_uuid.uuid4().hex[:6]}")
    auditor = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"auditor-{_uuid.uuid4().hex[:6]}@test.org",
        password="AuditorPass1!",
        display_name="Auditor User",
        role_code="auditor",
        profile_type="staff",
    )
    await db_session.commit()

    admin_token = await login(client, admin["user"].email, admin["password"], admin["tenant"].slug)
    auditor_token = await login(client, auditor["user"].email, auditor["password"], admin["tenant"].slug)

    profile = await _create_profile(
        client,
        admin_token,
        member_code="AUD-001",
        display_name="Audit Member",
        email="audit-member@test.org",
    )
    await _create_contribution(
        client,
        admin_token,
        membership_profile_id=profile["id"],
    )

    contribution_list = await client.get(
        "/api/v1/contributions/",
        headers={"Authorization": f"Bearer {auditor_token}"},
    )
    assert contribution_list.status_code == 200, contribution_list.text
    assert len(contribution_list.json()) == 1

    summary = await client.get(
        "/api/v1/contributions/summary?year=2026",
        headers={"Authorization": f"Bearer {auditor_token}"},
    )
    assert summary.status_code == 200, summary.text
    assert summary.json()["total_expected"] == "120.00"

    payments = await client.get(
        "/api/v1/contributions/payments",
        headers={"Authorization": f"Bearer {auditor_token}"},
    )
    assert payments.status_code == 200, payments.text

    audit_events = await client.get(
        "/api/v1/admin/audit/events",
        headers={"Authorization": f"Bearer {auditor_token}"},
    )
    assert audit_events.status_code == 200, audit_events.text

    report_export = await client.get(
        "/api/v1/contributions/report/export",
        headers={"Authorization": f"Bearer {auditor_token}"},
    )
    assert report_export.status_code == 200, report_export.text
    assert report_export.headers["content-type"] == "text/csv; charset=utf-8"

    blocked_create = await client.post(
        "/api/v1/contributions/",
        headers={"Authorization": f"Bearer {auditor_token}"},
        json={
            "membership_profile_id": profile["id"],
            "year": 2027,
            "expected_amount": "50.00",
            "paid_amount": "0.00",
            "currency": "EUR",
            "status": "pending",
        },
    )
    assert blocked_create.status_code == 403, blocked_create.text

    treasurer = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"treasurer-export-{_uuid.uuid4().hex[:6]}@test.org",
        password="TreasurerPass1!",
        display_name="Treasurer Export",
        role_code="treasurer",
        profile_type="staff",
    )
    await db_session.commit()
    treasurer_token = await login(client, treasurer["user"].email, treasurer["password"], admin["tenant"].slug)

    blocked_report = await client.get(
        "/api/v1/contributions/report/export",
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )
    assert blocked_report.status_code == 403, blocked_report.text


async def test_censor_can_manage_disciplinary_records_and_treasurer_cannot(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"censor-admin-{_uuid.uuid4().hex[:6]}")
    censor = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"censor-{_uuid.uuid4().hex[:6]}@test.org",
        password="CensorPass1!",
        display_name="Censor User",
        role_code="censor",
        profile_type="staff",
    )
    treasurer = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"treasurer-{_uuid.uuid4().hex[:6]}@test.org",
        password="TreasurerPass2!",
        display_name="Treasurer User",
        role_code="treasurer",
        profile_type="staff",
    )
    await db_session.commit()

    admin_token = await login(client, admin["user"].email, admin["password"], admin["tenant"].slug)
    censor_token = await login(client, censor["user"].email, censor["password"], admin["tenant"].slug)
    treasurer_token = await login(client, treasurer["user"].email, treasurer["password"], admin["tenant"].slug)

    profile = await _create_profile(
        client,
        admin_token,
        member_code="DISC-001",
        display_name="Disciplined Member",
        email="discipline@test.org",
    )
    policy = await client.post(
        "/api/v1/policies/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Conduct Rule", "category": "conduct", "status": "published"},
    )
    assert policy.status_code == 201, policy.text

    allowed = await client.post(
        "/api/v1/disciplinary/",
        headers={"Authorization": f"Bearer {censor_token}"},
        json={
            "membership_profile_id": profile["id"],
            "policy_record_id": policy.json()["id"],
            "title": "Code Reminder",
            "amount": "10.00",
            "currency": "EUR",
            "status": "under_review",
        },
    )
    assert allowed.status_code == 201, allowed.text

    blocked = await client.post(
        "/api/v1/disciplinary/",
        headers={"Authorization": f"Bearer {treasurer_token}"},
        json={
            "membership_profile_id": profile["id"],
            "title": "Should Fail",
            "amount": "10.00",
            "currency": "EUR",
            "status": "open",
        },
    )
    assert blocked.status_code == 403, blocked.text


async def test_principal_admin_keeps_tenant_administration_access(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_tenant_with_user(db_session, f"pa-admin-{_uuid.uuid4().hex[:6]}")
    principal_admin = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"principal-{_uuid.uuid4().hex[:6]}@test.org",
        password="PrincipalPass1!",
        display_name="Principal Admin",
        role_code="principal_admin",
        profile_type="admin",
    )
    await db_session.commit()

    admin_token = await login(client, admin["user"].email, admin["password"], admin["tenant"].slug)
    principal_token = await login(
        client,
        principal_admin["user"].email,
        principal_admin["password"],
        admin["tenant"].slug,
    )

    create_event = await client.post(
        "/api/v1/events/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Admin Seeded Event",
            "start_at": "2026-09-01T10:00:00Z",
            "end_at": "2026-09-01T12:00:00Z",
            "visibility_scope": "tenant_public",
            "status": "published",
        },
    )
    assert create_event.status_code == 201, create_event.text

    settings = await client.put(
        f"/api/v1/tenants/{admin['tenant'].id}/settings",
        headers={"Authorization": f"Bearer {principal_token}"},
        json={"name": "Principal Managed Org"},
    )
    assert settings.status_code == 200, settings.text
    assert settings.json()["name"] == "Principal Managed Org"

    export = await client.get(
        "/api/v1/events/export",
        headers={"Authorization": f"Bearer {principal_token}"},
    )
    assert export.status_code == 200, export.text
