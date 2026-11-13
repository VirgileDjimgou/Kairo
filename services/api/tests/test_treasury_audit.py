"""F1 auditability: expense ledger, auditor access, receipts and exercise closing."""

import uuid

import pytest
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


async def _finance_tenant(db_session: AsyncSession, suffix: str) -> dict:
    admin = await create_tenant_with_user(db_session, suffix)
    people = {"admin": admin}
    for role, prefix in (("treasurer", "treasurer"), ("auditor", "auditor"), ("member", "member")):
        people[role] = await create_user_for_tenant(
            db_session,
            tenant_id=admin["tenant"].id,
            email=f"{prefix}.{suffix}@test.org",
            password="FinancePass123!",
            display_name=f"{prefix.title()} {suffix}",
            role_code=role,
            profile_type="staff" if role != "member" else "member",
            member_code=f"F1-{suffix[:4].upper()}-{prefix[:3].upper()}",
        )
    await db_session.commit()
    return people


async def _headers(client: AsyncClient, person: dict, slug: str) -> dict:
    token = await login(client, person["user"].email, person["password"], slug)
    return {"Authorization": f"Bearer {token}"}


async def _profile_id(client: AsyncClient, headers: dict, suffix: str) -> str:
    response = await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": f"F1P-{suffix[:6].upper()}",
            "first_name": "Audit",
            "last_name": "Member",
            "display_name": "Audit Member",
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def _create_expense(
    client: AsyncClient,
    headers: dict,
    *,
    amount: str = "25.00",
    category: str = "administration",
    spent_at: str = "2026-06-01T12:00:00Z",
) -> dict:
    response = await client.post(
        "/api/v1/contributions/expenses",
        json={
            "category": category,
            "amount": amount,
            "spent_at": spent_at,
            "description": f"Expense {category}",
            "payee": "Supplier",
            "payment_method": "bank_transfer",
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_expense_ledger_is_readable_filterable_and_exportable(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _finance_tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)

    administration = await _create_expense(client, treasurer, amount="25.00")
    tournament = await _create_expense(
        client, treasurer, amount="80.00", category="tournament"
    )
    await _create_expense(
        client,
        treasurer,
        amount="40.00",
        spent_at="2025-06-01T12:00:00Z",
    )

    listed = await client.get(
        "/api/v1/contributions/expenses", params={"year": 2026}, headers=treasurer
    )
    assert listed.status_code == 200, listed.text
    assert {row["id"] for row in listed.json()} == {
        administration["id"],
        tournament["id"],
    }

    filtered = await client.get(
        "/api/v1/contributions/expenses",
        params={"year": 2026, "category": "tournament"},
        headers=treasurer,
    )
    assert [row["id"] for row in filtered.json()] == [tournament["id"]]

    detail = await client.get(
        f"/api/v1/contributions/expenses/{administration['id']}", headers=treasurer
    )
    assert detail.status_code == 200
    assert detail.json()["description"] == "Expense administration"

    csv_export = await client.get(
        "/api/v1/contributions/expenses/export",
        params={"year": 2026, "export_format": "csv"},
        headers=treasurer,
    )
    assert csv_export.status_code == 200, csv_export.text
    assert "administration" in csv_export.text
    assert "tournament" in csv_export.text
    assert "40.00" not in csv_export.text

    xlsx_export = await client.get(
        "/api/v1/contributions/expenses/export",
        params={"year": 2026, "export_format": "xlsx"},
        headers=treasurer,
    )
    assert xlsx_export.status_code == 200, xlsx_export.text
    assert xlsx_export.content[:2] == b"PK"


async def test_auditor_can_read_budget_and_expense_ledger(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _finance_tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)
    auditor = await _headers(client, people["auditor"], slug)
    member = await _headers(client, people["member"], slug)

    await _create_expense(client, treasurer, amount="30.00")

    budget = await client.get(
        "/api/v1/contributions/annual-budget", params={"year": 2026}, headers=auditor
    )
    assert budget.status_code == 200, budget.text
    assert budget.json()["expense_total"] == "30.00"

    expenses = await client.get(
        "/api/v1/contributions/expenses", params={"year": 2026}, headers=auditor
    )
    assert expenses.status_code == 200, expenses.text
    assert len(expenses.json()) == 1

    forbidden_budget = await client.get(
        "/api/v1/contributions/annual-budget", params={"year": 2026}, headers=member
    )
    assert forbidden_budget.status_code == 403
    forbidden_expenses = await client.get(
        "/api/v1/contributions/expenses", params={"year": 2026}, headers=member
    )
    assert forbidden_expenses.status_code == 403


async def test_expense_receipt_can_be_attached_and_downloaded_by_auditor(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _finance_tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)
    auditor = await _headers(client, people["auditor"], slug)
    member = await _headers(client, people["member"], slug)
    expense = await _create_expense(client, treasurer)

    payload = b"%PDF-1.4 simplified receipt"
    uploaded = await client.post(
        f"/api/v1/contributions/expenses/{expense['id']}/attachment",
        files={"file": ("invoice.pdf", payload, "application/pdf")},
        headers=treasurer,
    )
    assert uploaded.status_code == 200, uploaded.text
    assert uploaded.json()["attachment_file_name"] == "invoice.pdf"
    assert uploaded.json()["attachment_content_type"] == "application/pdf"

    downloaded = await client.get(
        f"/api/v1/contributions/expenses/{expense['id']}/attachment",
        headers=auditor,
    )
    assert downloaded.status_code == 200, downloaded.text
    assert downloaded.content == payload
    assert downloaded.headers["content-type"].startswith("application/pdf")

    forbidden = await client.get(
        f"/api/v1/contributions/expenses/{expense['id']}/attachment", headers=member
    )
    assert forbidden.status_code == 403

    invalid = await client.post(
        f"/api/v1/contributions/expenses/{expense['id']}/attachment",
        files={"file": ("notes.txt", b"plain text", "text/plain")},
        headers=treasurer,
    )
    assert invalid.status_code == 422


async def test_closing_an_exercise_blocks_writes_until_reopened(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _finance_tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)
    admin = await _headers(client, people["admin"], slug)

    profile_id = await _profile_id(client, treasurer, suffix)
    contribution = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": profile_id,
            "year": 2026,
            "expected_amount": "100.00",
        },
        headers=treasurer,
    )
    assert contribution.status_code == 201, contribution.text

    closed = await client.post(
        "/api/v1/contributions/periods/2026/close", headers=treasurer
    )
    assert closed.status_code == 200, closed.text
    assert closed.json()["status"] == "closed"

    blocked_payment = await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": contribution.json()["id"],
            "amount": "50.00",
            "paid_at": "2026-08-01T12:00:00Z",
        },
        headers=treasurer,
    )
    assert blocked_payment.status_code == 409

    blocked_expense = await client.post(
        "/api/v1/contributions/expenses",
        json={
            "category": "administration",
            "amount": "10.00",
            "spent_at": "2026-09-01T12:00:00Z",
            "description": "Postage",
        },
        headers=treasurer,
    )
    assert blocked_expense.status_code == 409

    blocked_contribution = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": profile_id,
            "year": 2026,
            "expected_amount": "20.00",
        },
        headers=treasurer,
    )
    assert blocked_contribution.status_code == 409

    next_year = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": profile_id,
            "year": 2027,
            "expected_amount": "20.00",
        },
        headers=treasurer,
    )
    assert next_year.status_code == 201, next_year.text

    # Reopening is reserved to tenant administration.
    assert (
        await client.post(
            "/api/v1/contributions/periods/2026/reopen",
            json={"reason": "Late payment"},
            headers=treasurer,
        )
    ).status_code == 403
    reopened = await client.post(
        "/api/v1/contributions/periods/2026/reopen",
        json={"reason": "Late bank transfer received"},
        headers=admin,
    )
    assert reopened.status_code == 200, reopened.text
    assert reopened.json()["status"] == "open"

    payment = await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": contribution.json()["id"],
            "amount": "50.00",
            "paid_at": "2026-08-01T12:00:00Z",
        },
        headers=treasurer,
    )
    assert payment.status_code == 201, payment.text

    period = await client.get(
        "/api/v1/contributions/periods/2026", headers=treasurer
    )
    assert period.status_code == 200
    assert period.json()["status"] == "open"
