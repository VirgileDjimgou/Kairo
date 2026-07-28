"""Integration coverage for the declared cash receipt workflow."""

import uuid

import pytest
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_office_receipt_declaration_requires_treasurer_validation(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    admin = await create_tenant_with_user(db_session, f"receipts-{uuid.uuid4().hex[:6]}")
    vice_president = await create_user_for_tenant(
        db_session, tenant_id=admin["tenant"].id, email="vice.receipt@test.org",
        password="VicePass123!", display_name="Vice Receipt", role_code="vice_president", profile_type="staff",
    )
    treasurer = await create_user_for_tenant(
        db_session, tenant_id=admin["tenant"].id, email="treasurer.receipt@test.org",
        password="TreasurerPass123!", display_name="Treasurer Receipt", role_code="treasurer", profile_type="staff",
    )
    member = await create_user_for_tenant(
        db_session, tenant_id=admin["tenant"].id, email="marie.receipt@test.org",
        password="MemberPass123!", display_name="Marie Dupont", role_code="member", profile_type="member", member_code="MAR-001",
    )
    await db_session.commit()

    admin_token = await login(client, admin["user"].email, admin["password"], admin["tenant"].slug)
    vice_token = await login(client, vice_president["user"].email, vice_president["password"], admin["tenant"].slug)
    treasurer_token = await login(client, treasurer["user"].email, treasurer["password"], admin["tenant"].slug)
    member_token = await login(client, member["user"].email, member["password"], admin["tenant"].slug)

    member_options = await client.get(
        "/api/v1/contributions/receipt-declarations/member-options",
        headers={"Authorization": f"Bearer {vice_token}"},
    )
    assert member_options.status_code == 200, member_options.text
    selected_option = next(item for item in member_options.json() if item["id"] == str(member["profile"].id))
    assert selected_option["display_name"] == "Marie Dupont"
    assert selected_option["email"] == "marie.receipt@test.org"
    assert selected_option["membership_type"] == "individual"
    assert "tenant_id" not in selected_option
    assert "user_id" not in selected_option
    assert (await client.get(
        "/api/v1/contributions/receipt-declarations/member-options",
        headers={"Authorization": f"Bearer {member_token}"},
    )).status_code == 403

    contribution = await client.post(
        "/api/v1/contributions/", json={
            "membership_profile_id": str(member["profile"].id), "year": 2026,
            "expected_amount": "60.00", "paid_amount": "0.00", "currency": "EUR",
        }, headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert contribution.status_code == 201, contribution.text

    declaration = await client.post(
        "/api/v1/contributions/receipt-declarations", json={
            "membership_profile_id": str(member["profile"].id), "amount": "20.00",
            "currency": "EUR", "payment_method": "cash", "note": "Cash received from Marie",
        }, headers={"Authorization": f"Bearer {vice_token}"},
    )
    assert declaration.status_code == 201, declaration.text
    declaration_id = declaration.json()["id"]
    assert declaration.json()["status"] == "draft"

    submit = await client.post(
        f"/api/v1/contributions/receipt-declarations/{declaration_id}/submit",
        headers={"Authorization": f"Bearer {vice_token}"},
    )
    assert submit.status_code == 200, submit.text
    assert submit.json()["status"] == "submitted"

    member_pending = await client.get(
        "/api/v1/contributions/receipt-declarations/me", headers={"Authorization": f"Bearer {member_token}"}
    )
    assert member_pending.status_code == 200
    assert member_pending.json()[0]["status"] == "submitted"
    balance_before = await client.get(
        f"/api/v1/memberships/{member['profile'].id}/balance", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert balance_before.json()["total_balance"] == "60.00"

    forbidden = await client.post(
        f"/api/v1/contributions/receipt-declarations/{declaration_id}/process",
        json={"action": "validated", "contribution_record_id": contribution.json()["id"]},
        headers={"Authorization": f"Bearer {vice_token}"},
    )
    assert forbidden.status_code == 403

    processed = await client.post(
        f"/api/v1/contributions/receipt-declarations/{declaration_id}/process",
        json={"action": "validated", "contribution_record_id": contribution.json()["id"]},
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )
    assert processed.status_code == 200, processed.text
    assert processed.json()["status"] == "validated"
    assert processed.json()["processed_amount"] == "20.00"
    assert processed.json()["payment_record_id"] is not None

    balance_after = await client.get(
        f"/api/v1/memberships/{member['profile'].id}/balance", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert balance_after.json()["total_paid"] == "20.00"
    assert balance_after.json()["total_balance"] == "40.00"


@pytest.mark.asyncio
async def test_member_cannot_declare_receipt_and_auditor_can_declare(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    admin = await create_tenant_with_user(db_session, f"auditor-receipt-{uuid.uuid4().hex[:6]}")
    auditor = await create_user_for_tenant(
        db_session, tenant_id=admin["tenant"].id, email="auditor.receipt@test.org",
        password="AuditorPass123!", display_name="Auditor Receipt", role_code="auditor", profile_type="staff",
    )
    member = await create_user_for_tenant(
        db_session, tenant_id=admin["tenant"].id, email="member.receipt@test.org",
        password="MemberPass123!", display_name="Member Receipt", role_code="member", profile_type="member", member_code="MEM-001",
    )
    await db_session.commit()
    auditor_token = await login(client, auditor["user"].email, auditor["password"], admin["tenant"].slug)
    member_token = await login(client, member["user"].email, member["password"], admin["tenant"].slug)
    payload = {"membership_profile_id": str(member["profile"].id), "amount": "10.00"}
    assert (await client.post("/api/v1/contributions/receipt-declarations", json=payload, headers={"Authorization": f"Bearer {auditor_token}"})).status_code == 201
    assert (await client.post("/api/v1/contributions/receipt-declarations", json=payload, headers={"Authorization": f"Bearer {member_token}"})).status_code == 403
