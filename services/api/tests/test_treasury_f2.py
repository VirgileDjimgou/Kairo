"""F2 treasury completeness: receipt dates, numbered receipts, position and plan."""

import uuid

import pytest
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


async def _tenant(db_session: AsyncSession, suffix: str) -> dict:
    admin = await create_tenant_with_user(db_session, suffix)
    treasurer = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"treasurer.f2.{suffix}@test.org",
        password="FinancePass123!",
        display_name="Treasurer F2",
        role_code="treasurer",
        profile_type="staff",
    )
    member = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"member.f2.{suffix}@test.org",
        password="FinancePass123!",
        display_name="Member F2",
        role_code="member",
        profile_type="member",
        member_code=f"F2-{suffix[:6].upper()}",
    )
    other = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"other.f2.{suffix}@test.org",
        password="FinancePass123!",
        display_name="Other F2",
        role_code="member",
        profile_type="member",
        member_code=f"F2O-{suffix[:6].upper()}",
    )
    await db_session.commit()
    return {"admin": admin, "treasurer": treasurer, "member": member, "other": other}


async def _headers(client: AsyncClient, person: dict, slug: str) -> dict:
    token = await login(client, person["user"].email, person["password"], slug)
    return {"Authorization": f"Bearer {token}"}


async def _contribution(
    client: AsyncClient, headers: dict, profile_id: str, year: int, expected: str = "100.00"
) -> dict:
    response = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": profile_id,
            "year": year,
            "expected_amount": expected,
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_receipt_payment_uses_the_real_receipt_date(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)
    contribution = await _contribution(
        client, treasurer, str(people["member"]["profile"].id), 2025
    )

    declared = await client.post(
        "/api/v1/contributions/receipt-declarations",
        json={
            "income_type": "membership_contribution",
            "membership_profile_id": str(people["member"]["profile"].id),
            "amount": "40.00",
            "received_at": "2025-12-31T10:00:00Z",
            "payment_method": "cash",
        },
        headers=treasurer,
    )
    assert declared.status_code == 201, declared.text
    declaration_id = declared.json()["id"]
    assert (
        await client.post(
            f"/api/v1/contributions/receipt-declarations/{declaration_id}/submit",
            headers=treasurer,
        )
    ).status_code == 200
    validated = await client.post(
        f"/api/v1/contributions/receipt-declarations/{declaration_id}/process",
        json={"action": "validated", "contribution_record_id": contribution["id"]},
        headers=treasurer,
    )
    assert validated.status_code == 200, validated.text

    payments = await client.get(
        f"/api/v1/contributions/{contribution['id']}/payments", headers=treasurer
    )
    assert len(payments.json()) == 1
    assert payments.json()[0]["paid_at"].startswith("2025-12-31")
    assert payments.json()[0]["receipt_number"] == "2025-00001"

    budget_2025 = await client.get(
        "/api/v1/contributions/annual-budget", params={"year": 2025}, headers=treasurer
    )
    budget_2026 = await client.get(
        "/api/v1/contributions/annual-budget", params={"year": 2026}, headers=treasurer
    )
    assert budget_2025.json()["income_total"] == "40.00"
    assert budget_2026.json()["income_total"] == "0.00"


async def test_payment_receipts_are_numbered_and_access_scoped(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)
    owner = await _headers(client, people["member"], slug)
    other = await _headers(client, people["other"], slug)
    contribution = await _contribution(
        client, treasurer, str(people["member"]["profile"].id), 2026
    )

    first = await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": contribution["id"],
            "amount": "60.00",
            "paid_at": "2026-03-01T12:00:00Z",
            "payment_method": "cash",
        },
        headers=treasurer,
    )
    second = await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": contribution["id"],
            "amount": "40.00",
            "paid_at": "2026-04-01T12:00:00Z",
            "payment_method": "cash",
        },
        headers=treasurer,
    )
    assert first.status_code == 201, first.text
    assert second.status_code == 201, second.text
    assert first.json()["receipt_number"] == "2026-00001"
    assert second.json()["receipt_number"] == "2026-00002"

    receipt = await client.get(
        f"/api/v1/contributions/payments/{first.json()['id']}/receipt.pdf",
        headers=treasurer,
    )
    assert receipt.status_code == 200, receipt.text
    assert receipt.content.startswith(b"%PDF")

    own_receipt = await client.get(
        f"/api/v1/contributions/payments/{first.json()['id']}/receipt.pdf",
        headers=owner,
    )
    assert own_receipt.status_code == 200

    forbidden = await client.get(
        f"/api/v1/contributions/payments/{first.json()['id']}/receipt.pdf",
        headers=other,
    )
    assert forbidden.status_code == 403

    reversed_payment = await client.post(
        f"/api/v1/contributions/payments/{second.json()['id']}/reverse",
        json={"reason": "Duplicate cash entry"},
        headers=treasurer,
    )
    assert reversed_payment.status_code == 200
    reversed_receipt = await client.get(
        f"/api/v1/contributions/payments/{second.json()['id']}/receipt.pdf",
        headers=treasurer,
    )
    assert reversed_receipt.status_code == 409


async def test_treasury_position_combines_opening_balances_and_accounts(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)
    profile_id = str(people["member"]["profile"].id)

    accounts = await client.get("/api/v1/contributions/accounts", headers=treasurer)
    assert accounts.status_code == 200, accounts.text
    assert {account["kind"] for account in accounts.json()} == {"cash", "bank"}
    cash = next(account for account in accounts.json() if account["kind"] == "cash")
    bank = next(account for account in accounts.json() if account["kind"] == "bank")

    opening_cash = await client.put(
        f"/api/v1/contributions/accounts/{cash['id']}/opening-balance/2026",
        json={"amount": "100.00"},
        headers=treasurer,
    )
    opening_bank = await client.put(
        f"/api/v1/contributions/accounts/{bank['id']}/opening-balance/2026",
        json={"amount": "500.00"},
        headers=treasurer,
    )
    assert opening_cash.status_code == 200, opening_cash.text
    assert opening_bank.status_code == 200, opening_bank.text

    # A prior-year cash payment must carry into the 2026 opening balance.
    contribution_2025 = await _contribution(client, treasurer, profile_id, 2025)
    previous_payment = await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": contribution_2025["id"],
            "amount": "20.00",
            "paid_at": "2025-11-01T12:00:00Z",
            "payment_method": "cash",
        },
        headers=treasurer,
    )
    assert previous_payment.status_code == 201, previous_payment.text

    contribution_2026 = await _contribution(client, treasurer, profile_id, 2026)
    payment = await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": contribution_2026["id"],
            "amount": "50.00",
            "paid_at": "2026-03-01T12:00:00Z",
            "payment_method": "cash",
        },
        headers=treasurer,
    )
    assert payment.status_code == 201, payment.text
    expense = await client.post(
        "/api/v1/contributions/expenses",
        json={
            "category": "administration",
            "amount": "30.00",
            "spent_at": "2026-04-01T12:00:00Z",
            "description": "Office supplies",
            "payment_method": "bank_transfer",
        },
        headers=treasurer,
    )
    assert expense.status_code == 201, expense.text

    position = await client.get(
        "/api/v1/contributions/treasury-position",
        params={"year": 2026},
        headers=treasurer,
    )
    assert position.status_code == 200, position.text
    body = position.json()
    by_kind = {row["kind"]: row for row in body["accounts"]}
    assert by_kind["cash"]["opening_balance"] == "100.00"
    assert by_kind["cash"]["inflow"] == "50.00"
    assert by_kind["cash"]["closing_balance"] == "150.00"
    assert by_kind["bank"]["opening_balance"] == "500.00"
    assert by_kind["bank"]["outflow"] == "30.00"
    assert by_kind["bank"]["closing_balance"] == "470.00"
    assert body["total_closing"] == "620.00"

    # Without an explicit opening, the next exercise carries the previous closing.
    next_position = await client.get(
        "/api/v1/contributions/treasury-position",
        params={"year": 2027},
        headers=treasurer,
    )
    assert next_position.status_code == 200, next_position.text
    next_by_kind = {row["kind"]: row for row in next_position.json()["accounts"]}
    assert next_by_kind["cash"]["opening_balance"] == "150.00"
    assert next_by_kind["bank"]["opening_balance"] == "470.00"
    assert next_position.json()["total_closing"] == "620.00"


async def test_voted_budget_plan_exposes_variance(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)
    profile_id = str(people["member"]["profile"].id)

    plan = await client.put(
        "/api/v1/contributions/budget-plan/2026",
        json={
            "lines": [
                {"direction": "income", "category": "membership_contribution", "planned_amount": "1000.00"},
                {"direction": "income", "category": "donation", "planned_amount": "200.00"},
                {"direction": "expense", "category": "administration", "planned_amount": "300.00"},
            ]
        },
        headers=treasurer,
    )
    assert plan.status_code == 200, plan.text
    assert plan.json()["planned_income_total"] == "1200.00"
    assert plan.json()["planned_expense_total"] == "300.00"

    contribution = await _contribution(client, treasurer, profile_id, 2026)
    await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": contribution["id"],
            "amount": "900.00",
            "paid_at": "2026-05-01T12:00:00Z",
            "payment_method": "bank_transfer",
        },
        headers=treasurer,
    )
    await client.post(
        "/api/v1/contributions/expenses",
        json={
            "category": "administration",
            "amount": "320.00",
            "spent_at": "2026-05-02T12:00:00Z",
            "description": "Printing",
            "payment_method": "bank_transfer",
        },
        headers=treasurer,
    )

    budget = await client.get(
        "/api/v1/contributions/annual-budget", params={"year": 2026}, headers=treasurer
    )
    assert budget.status_code == 200, budget.text
    body = budget.json()
    assert body["planned_income_total"] == "1200.00"
    assert body["planned_expense_total"] == "300.00"
    assert body["income_variance"] == "-300.00"
    assert body["expense_variance"] == "20.00"
    income = {row["category"]: row for row in body["income_by_category"]}
    assert income["membership_contribution"]["planned_amount"] == "1000.00"
    assert income["membership_contribution"]["variance"] == "-100.00"

    invalid = await client.put(
        "/api/v1/contributions/budget-plan/2026",
        json={"lines": [{"direction": "income", "category": "not_a_category", "planned_amount": "10.00"}]},
        headers=treasurer,
    )
    assert invalid.status_code == 422

    duplicate = await client.put(
        "/api/v1/contributions/budget-plan/2026",
        json={
            "lines": [
                {"direction": "income", "category": "donation", "planned_amount": "10.00"},
                {"direction": "income", "category": "donation", "planned_amount": "20.00"},
            ]
        },
        headers=treasurer,
    )
    assert duplicate.status_code == 422

    await client.post("/api/v1/contributions/periods/2026/close", headers=treasurer)
    blocked = await client.put(
        "/api/v1/contributions/budget-plan/2026",
        json={"lines": [{"direction": "income", "category": "donation", "planned_amount": "10.00"}]},
        headers=treasurer,
    )
    assert blocked.status_code == 409
