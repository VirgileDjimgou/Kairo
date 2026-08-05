"""Integration coverage for treasurer-only expense recording and annual budget totals."""

import uuid

import pytest
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_treasurer_records_expense_and_budget_groups_realized_flows(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    admin = await create_tenant_with_user(db_session, f"expenses-{uuid.uuid4().hex[:6]}")
    treasurer = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email="treasurer.expenses@test.org",
        password="TreasurerPass123!",
        display_name="Treasurer Expenses",
        role_code="treasurer",
        profile_type="staff",
    )
    president = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email="president.expenses@test.org",
        password="PresidentPass123!",
        display_name="President Expenses",
        role_code="president",
        profile_type="staff",
    )
    member = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email="member.expenses@test.org",
        password="MemberPass123!",
        display_name="Member Expenses",
        role_code="member",
        profile_type="member",
        member_code="EXP-001",
    )
    await db_session.commit()

    admin_token = await login(client, admin["user"].email, admin["password"], admin["tenant"].slug)
    treasurer_token = await login(client, treasurer["user"].email, treasurer["password"], admin["tenant"].slug)
    president_token = await login(client, president["user"].email, president["password"], admin["tenant"].slug)

    contribution = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": str(member["profile"].id),
            "year": 2026,
            "expected_amount": "60.00",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert contribution.status_code == 201, contribution.text
    payment = await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": contribution.json()["id"],
            "amount": "60.00",
            "paid_at": "2026-08-05T12:00:00Z",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert payment.status_code == 201, payment.text

    donation = await client.post(
        "/api/v1/contributions/receipt-declarations",
        json={"income_type": "donation", "source_name": "Local supporter", "amount": "40.00"},
        headers={"Authorization": f"Bearer {president_token}"},
    )
    assert donation.status_code == 201, donation.text
    donation_id = donation.json()["id"]
    assert (await client.post(
        f"/api/v1/contributions/receipt-declarations/{donation_id}/submit",
        headers={"Authorization": f"Bearer {president_token}"},
    )).status_code == 200
    assert (await client.post(
        f"/api/v1/contributions/receipt-declarations/{donation_id}/process",
        json={"action": "validated"},
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )).status_code == 200

    forbidden_for_president = await client.post(
        "/api/v1/contributions/expenses",
        json={"category": "fuel_transport", "amount": "10.00", "description": "Fuel"},
        headers={"Authorization": f"Bearer {president_token}"},
    )
    assert forbidden_for_president.status_code == 403
    forbidden_for_legacy_admin = await client.post(
        "/api/v1/contributions/expenses",
        json={"category": "fuel_transport", "amount": "10.00", "description": "Fuel"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert forbidden_for_legacy_admin.status_code == 403

    expense = await client.post(
        "/api/v1/contributions/expenses",
        json={
            "category": "sport_equipment",
            "amount": "25.00",
            "spent_at": "2026-08-05T12:00:00Z",
            "description": "Training balls",
            "payee": "Sports supplier",
            "payment_method": "card",
        },
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )
    assert expense.status_code == 201, expense.text
    assert expense.json()["category"] == "sport_equipment"
    assert expense.json()["amount"] == "25.00"

    budget = await client.get(
        "/api/v1/contributions/annual-budget?year=2026",
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )
    assert budget.status_code == 200, budget.text
    assert budget.json()["income_total"] == "100.00"
    assert budget.json()["expense_total"] == "25.00"
    assert budget.json()["available_balance"] == "75.00"
    assert {item["category"]: item["amount"] for item in budget.json()["income_by_category"]}["donation"] == "40.00"
    assert {item["category"]: item["amount"] for item in budget.json()["expenses_by_category"]}["sport_equipment"] == "25.00"
    assert budget.json()["recent_expenses"][0]["description"] == "Training balls"

    assert (await client.get(
        "/api/v1/contributions/annual-budget?year=2026",
        headers={"Authorization": f"Bearer {president_token}"},
    )).status_code == 403
