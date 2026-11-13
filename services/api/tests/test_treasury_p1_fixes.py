"""Regression coverage for the five P1 treasury correctness fixes."""

import csv
import io
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
        email=f"treasurer.p1.{suffix}@test.org",
        password="FinancePass123!",
        display_name="Treasurer P1",
        role_code="treasurer",
        profile_type="staff",
    )
    member = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"member.p1.{suffix}@test.org",
        password="FinancePass123!",
        display_name="Member P1",
        role_code="member",
        profile_type="member",
        member_code=f"P1-{suffix[:6].upper()}",
    )
    await db_session.commit()
    return {"admin": admin, "treasurer": treasurer, "member": member}


async def _headers(client: AsyncClient, person: dict, slug: str) -> dict:
    token = await login(client, person["user"].email, person["password"], slug)
    return {"Authorization": f"Bearer {token}"}


async def _contribution(
    client: AsyncClient, headers: dict, profile_id: str, year: int
) -> dict:
    response = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": profile_id,
            "year": year,
            "expected_amount": "100.00",
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _declare_and_validate(
    client: AsyncClient,
    headers: dict,
    *,
    payload: dict,
    contribution_id: str | None = None,
) -> dict:
    declared = await client.post(
        "/api/v1/contributions/receipt-declarations",
        json=payload,
        headers=headers,
    )
    assert declared.status_code == 201, declared.text
    declaration_id = declared.json()["id"]
    submitted = await client.post(
        f"/api/v1/contributions/receipt-declarations/{declaration_id}/submit",
        headers=headers,
    )
    assert submitted.status_code == 200, submitted.text
    process_payload = {"action": "validated"}
    if contribution_id is not None:
        process_payload["contribution_record_id"] = contribution_id
    validated = await client.post(
        f"/api/v1/contributions/receipt-declarations/{declaration_id}/process",
        json=process_payload,
        headers=headers,
    )
    assert validated.status_code == 200, validated.text
    return validated.json()


async def test_non_membership_income_is_booked_in_the_receipt_year(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)

    await _declare_and_validate(
        client,
        treasurer,
        payload={
            "income_type": "donation",
            "source_name": "Year-end donor",
            "amount": "30.00",
            "received_at": "2025-12-31T10:00:00Z",
        },
    )

    budget_2025 = await client.get(
        "/api/v1/contributions/annual-budget", params={"year": 2025}, headers=treasurer
    )
    budget_2026 = await client.get(
        "/api/v1/contributions/annual-budget", params={"year": 2026}, headers=treasurer
    )
    assert budget_2025.json()["income_total"] == "30.00"
    assert budget_2026.json()["income_total"] == "0.00"

    journal = await client.get(
        "/api/v1/contributions/journal/export", params={"year": 2025}, headers=treasurer
    )
    rows = list(csv.DictReader(io.StringIO(journal.text)))
    donation = next(row for row in rows if row["type"] == "receipt_declaration")
    assert donation["date"] == "2025-12-31"
    assert donation["amount"] == "30.00"


async def test_cash_in_custody_is_excluded_from_the_available_position(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)
    contribution = await _contribution(
        client, treasurer, str(people["member"]["profile"].id), 2026
    )

    declaration = await _declare_and_validate(
        client,
        treasurer,
        payload={
            "income_type": "membership_contribution",
            "membership_profile_id": str(people["member"]["profile"].id),
            "amount": "50.00",
            "received_at": "2026-06-01T10:00:00Z",
            "payment_method": "cash",
        },
        contribution_id=contribution["id"],
    )

    position = await client.get(
        "/api/v1/contributions/treasury-position",
        params={"year": 2026},
        headers=treasurer,
    )
    assert position.status_code == 200, position.text
    cash = next(row for row in position.json()["accounts"] if row["kind"] == "cash")
    assert cash["inflow"] == "50.00"
    assert cash["pending_custody"] == "50.00"
    assert cash["closing_balance"] == "0.00"
    assert position.json()["total_closing"] == "0.00"

    confirmed = await client.post(
        f"/api/v1/contributions/receipt-declarations/{declaration['id']}/confirm-treasury-receipt",
        json={"method": "cash", "note": "Received in the cash box"},
        headers=treasurer,
    )
    assert confirmed.status_code == 200, confirmed.text

    after = await client.get(
        "/api/v1/contributions/treasury-position",
        params={"year": 2026},
        headers=treasurer,
    )
    cash_after = next(row for row in after.json()["accounts"] if row["kind"] == "cash")
    assert cash_after["pending_custody"] == "0.00"
    assert cash_after["closing_balance"] == "50.00"


async def test_expense_reversal_keeps_history_and_excludes_it_from_totals(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)

    expense = await client.post(
        "/api/v1/contributions/expenses",
        json={
            "category": "administration",
            "amount": "30.00",
            "spent_at": "2026-04-01T12:00:00Z",
            "description": "Wrong supplier",
            "payment_method": "bank_transfer",
        },
        headers=treasurer,
    )
    assert expense.status_code == 201, expense.text

    reversed_expense = await client.post(
        f"/api/v1/contributions/expenses/{expense.json()['id']}/reverse",
        json={"reason": "Invoice cancelled by the supplier"},
        headers=treasurer,
    )
    assert reversed_expense.status_code == 200, reversed_expense.text
    assert reversed_expense.json()["reversed_at"] is not None
    assert reversed_expense.json()["reversal_reason"] == "Invoice cancelled by the supplier"

    budget = await client.get(
        "/api/v1/contributions/annual-budget", params={"year": 2026}, headers=treasurer
    )
    assert budget.json()["expense_total"] == "0.00"

    position = await client.get(
        "/api/v1/contributions/treasury-position",
        params={"year": 2026},
        headers=treasurer,
    )
    assert position.json()["total_outflow"] == "0.00"

    listed = await client.get(
        "/api/v1/contributions/expenses", params={"year": 2026}, headers=treasurer
    )
    assert listed.json()[0]["reversed_at"] is not None

    export = await client.get(
        "/api/v1/contributions/expenses/export",
        params={"year": 2026, "export_format": "csv"},
        headers=treasurer,
    )
    assert "reversed" in export.text
    assert "Invoice cancelled by the supplier" in export.text

    again = await client.post(
        f"/api/v1/contributions/expenses/{expense.json()['id']}/reverse",
        json={"reason": "Second attempt"},
        headers=treasurer,
    )
    assert again.status_code == 409


async def test_closing_is_blocked_by_pending_declarations_and_handovers(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)
    profile_id = str(people["member"]["profile"].id)

    pending = await client.post(
        "/api/v1/contributions/receipt-declarations",
        json={
            "income_type": "donation",
            "source_name": "Pending donor",
            "amount": "15.00",
            "received_at": "2026-05-01T10:00:00Z",
        },
        headers=treasurer,
    )
    assert pending.status_code == 201, pending.text
    await client.post(
        f"/api/v1/contributions/receipt-declarations/{pending.json()['id']}/submit",
        headers=treasurer,
    )

    blocked = await client.post(
        "/api/v1/contributions/periods/2026/close", headers=treasurer
    )
    assert blocked.status_code == 409
    assert "pending" in blocked.json()["detail"].lower()

    await client.post(
        f"/api/v1/contributions/receipt-declarations/{pending.json()['id']}/process",
        json={"action": "rejected", "note": "No supporting document"},
        headers=treasurer,
    )
    closed = await client.post(
        "/api/v1/contributions/periods/2026/close", headers=treasurer
    )
    assert closed.status_code == 200, closed.text

    # A validated cash receipt awaiting handover also blocks the next close.
    contribution = await _contribution(client, treasurer, profile_id, 2027)
    declaration = await _declare_and_validate(
        client,
        treasurer,
        payload={
            "income_type": "membership_contribution",
            "membership_profile_id": profile_id,
            "amount": "25.00",
            "received_at": "2027-06-01T10:00:00Z",
            "payment_method": "cash",
        },
        contribution_id=contribution["id"],
    )
    blocked_handover = await client.post(
        "/api/v1/contributions/periods/2027/close", headers=treasurer
    )
    assert blocked_handover.status_code == 409
    assert "handover" in blocked_handover.json()["detail"].lower()

    await client.post(
        f"/api/v1/contributions/receipt-declarations/{declaration['id']}/confirm-treasury-receipt",
        json={"method": "cash"},
        headers=treasurer,
    )
    closed_2027 = await client.post(
        "/api/v1/contributions/periods/2027/close", headers=treasurer
    )
    assert closed_2027.status_code == 200, closed_2027.text


async def test_currency_cannot_change_when_a_budget_or_opening_balance_exists(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant(db_session, suffix)
    tenant = people["admin"]["tenant"]
    slug = tenant.slug
    admin = await _headers(client, people["admin"], slug)
    treasurer = await _headers(client, people["treasurer"], slug)

    plan = await client.put(
        "/api/v1/contributions/budget-plan/2026",
        json={
            "lines": [
                {
                    "direction": "expense",
                    "category": "administration",
                    "planned_amount": "200.00",
                }
            ]
        },
        headers=treasurer,
    )
    assert plan.status_code == 200, plan.text

    blocked_by_plan = await client.put(
        f"/api/v1/tenants/{tenant.id}/settings",
        json={"name": "Currency Lock", "default_language": "fr", "currency": "USD"},
        headers=admin,
    )
    assert blocked_by_plan.status_code == 409

    # A tenant with only an opening balance is locked too.
    suffix_two = uuid.uuid4().hex[:6]
    other = await _tenant(db_session, suffix_two)
    other_tenant = other["admin"]["tenant"]
    other_admin = await _headers(client, other["admin"], other_tenant.slug)
    other_treasurer = await _headers(client, other["treasurer"], other_tenant.slug)
    accounts = await client.get(
        "/api/v1/contributions/accounts", headers=other_treasurer
    )
    cash = next(account for account in accounts.json() if account["kind"] == "cash")
    opening = await client.put(
        f"/api/v1/contributions/accounts/{cash['id']}/opening-balance/2026",
        json={"amount": "10.00"},
        headers=other_treasurer,
    )
    assert opening.status_code == 200, opening.text
    blocked_by_opening = await client.put(
        f"/api/v1/tenants/{other_tenant.id}/settings",
        json={
            "name": "Currency Lock Two",
            "default_language": "fr",
            "currency": "USD",
        },
        headers=other_admin,
    )
    assert blocked_by_opening.status_code == 409


async def test_tenant_expense_categories_are_configurable(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)

    categories = await client.get(
        "/api/v1/contributions/expense-categories", headers=treasurer
    )
    assert categories.status_code == 200, categories.text
    assert {row["code"] for row in categories.json()} == {
        "sport_equipment",
        "fuel_transport",
        "tournament",
        "cultural_event",
        "administration",
        "other",
    }

    created = await client.post(
        "/api/v1/contributions/expense-categories",
        json={"name": "Insurance"},
        headers=treasurer,
    )
    assert created.status_code == 201, created.text
    custom_code = created.json()["code"]
    assert custom_code.startswith("custom_")

    expense = await client.post(
        "/api/v1/contributions/expenses",
        json={
            "category": custom_code,
            "amount": "120.00",
            "spent_at": "2026-07-01T12:00:00Z",
            "description": "Annual insurance",
            "payment_method": "bank_transfer",
        },
        headers=treasurer,
    )
    assert expense.status_code == 201, expense.text
    assert expense.json()["category"] == custom_code

    budget = await client.get(
        "/api/v1/contributions/annual-budget", params={"year": 2026}, headers=treasurer
    )
    assert budget.status_code == 200, budget.text
    by_category = {row["category"]: row for row in budget.json()["expenses_by_category"]}
    assert by_category[custom_code]["amount"] == "120.00"

    unknown = await client.post(
        "/api/v1/contributions/expenses",
        json={
            "category": "not_a_category",
            "amount": "10.00",
            "spent_at": "2026-07-02T12:00:00Z",
            "description": "Unknown category",
        },
        headers=treasurer,
    )
    assert unknown.status_code == 422


async def test_expense_approval_is_reserved_to_oversight_roles(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)
    auditor_user = await create_user_for_tenant(
        db_session,
        tenant_id=people["admin"]["tenant"].id,
        email=f"auditor.p1.{suffix}@test.org",
        password="FinancePass123!",
        display_name="Auditor P1",
        role_code="auditor",
        profile_type="staff",
    )
    president = await create_user_for_tenant(
        db_session,
        tenant_id=people["admin"]["tenant"].id,
        email=f"president.p1.{suffix}@test.org",
        password="FinancePass123!",
        display_name="President P1",
        role_code="president",
        profile_type="president",
    )
    await db_session.commit()
    president_headers = await _headers(client, president, slug)
    auditor = await _headers(client, auditor_user, slug)

    expense = await client.post(
        "/api/v1/contributions/expenses",
        json={
            "category": "administration",
            "amount": "40.00",
            "spent_at": "2026-08-01T12:00:00Z",
            "description": "Office supplies",
            "payment_method": "bank_transfer",
        },
        headers=treasurer,
    )
    assert expense.status_code == 201, expense.text
    assert expense.json()["status"] == "recorded"

    assert (
        await client.post(
            f"/api/v1/contributions/expenses/{expense.json()['id']}/approve",
            headers=treasurer,
        )
    ).status_code == 403
    assert (
        await client.post(
            f"/api/v1/contributions/expenses/{expense.json()['id']}/approve",
            headers=auditor,
        )
    ).status_code == 403

    approved = await client.post(
        f"/api/v1/contributions/expenses/{expense.json()['id']}/approve",
        headers=president_headers,
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "approved"
    assert approved.json()["approved_at"] is not None

    again = await client.post(
        f"/api/v1/contributions/expenses/{expense.json()['id']}/approve",
        headers=president_headers,
    )
    assert again.status_code == 409

    rejected_expense = await client.post(
        "/api/v1/contributions/expenses",
        json={
            "category": "administration",
            "amount": "15.00",
            "spent_at": "2026-08-02T12:00:00Z",
            "description": "Duplicate receipt",
            "payment_method": "cash",
        },
        headers=treasurer,
    )
    missing_note = await client.post(
        f"/api/v1/contributions/expenses/{rejected_expense.json()['id']}/reject",
        json={"note": ""},
        headers=president_headers,
    )
    assert missing_note.status_code == 422
    rejected = await client.post(
        f"/api/v1/contributions/expenses/{rejected_expense.json()['id']}/reject",
        json={"note": "Duplicate of an existing invoice"},
        headers=president_headers,
    )
    assert rejected.status_code == 200, rejected.text
    assert rejected.json()["status"] == "rejected"

    budget = await client.get(
        "/api/v1/contributions/annual-budget", params={"year": 2026}, headers=treasurer
    )
    assert budget.json()["expense_total"] == "40.00"


async def test_optional_separation_of_duties_blocks_self_validation(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant(db_session, suffix)
    tenant = people["admin"]["tenant"]
    slug = tenant.slug
    admin = await _headers(client, people["admin"], slug)
    treasurer = await _headers(client, people["treasurer"], slug)

    enabled = await client.put(
        f"/api/v1/tenants/{tenant.id}/settings",
        json={
            "name": "Separated Duties",
            "default_language": "fr",
            "finance": {"require_separate_receipt_validator": True},
        },
        headers=admin,
    )
    assert enabled.status_code == 200, enabled.text
    assert enabled.json()["finance"]["require_separate_receipt_validator"] is True

    declared = await client.post(
        "/api/v1/contributions/receipt-declarations",
        json={
            "income_type": "donation",
            "source_name": "Self validation donor",
            "amount": "20.00",
            "received_at": "2026-09-01T10:00:00Z",
        },
        headers=treasurer,
    )
    assert declared.status_code == 201, declared.text
    declaration_id = declared.json()["id"]
    await client.post(
        f"/api/v1/contributions/receipt-declarations/{declaration_id}/submit",
        headers=treasurer,
    )

    self_validation = await client.post(
        f"/api/v1/contributions/receipt-declarations/{declaration_id}/process",
        json={"action": "validated"},
        headers=treasurer,
    )
    assert self_validation.status_code == 403

    other_validation = await client.post(
        f"/api/v1/contributions/receipt-declarations/{declaration_id}/process",
        json={"action": "validated"},
        headers=admin,
    )
    assert other_validation.status_code == 200, other_validation.text
