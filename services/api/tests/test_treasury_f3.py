"""F3 treasury audit pack: idempotent import, journal export, safe reports."""

import csv
import io
import uuid

import pytest
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from openpyxl import load_workbook
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


async def _tenant(db_session: AsyncSession, suffix: str) -> dict:
    admin = await create_tenant_with_user(db_session, suffix)
    treasurer = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"treasurer.f3.{suffix}@test.org",
        password="FinancePass123!",
        display_name="Treasurer F3",
        role_code="treasurer",
        profile_type="staff",
    )
    member = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"member.f3.{suffix}@test.org",
        password="FinancePass123!",
        display_name="Member F3",
        role_code="member",
        profile_type="member",
        member_code=f"F3-{suffix[:6].upper()}",
    )
    await db_session.commit()
    return {"admin": admin, "treasurer": treasurer, "member": member}


async def _headers(client: AsyncClient, person: dict, slug: str) -> dict:
    token = await login(client, person["user"].email, person["password"], slug)
    return {"Authorization": f"Bearer {token}"}


async def test_csv_import_is_idempotent_and_duplicates_are_refused(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)
    member_code = people["member"]["profile"].member_code

    content = (
        "member_code,year,expected_amount,paid_amount,currency,status\n"
        f"{member_code},2026,100.00,40.00,EUR,partial\n"
    ).encode()

    first = await client.post(
        "/api/v1/contributions/import",
        files={"file": ("contributions.csv", content, "text/csv")},
        headers=treasurer,
    )
    assert first.status_code == 200, first.text
    assert first.json()["success_count"] == 1
    assert first.json()["skipped_count"] == 0

    replay = await client.post(
        "/api/v1/contributions/import",
        files={"file": ("contributions.csv", content, "text/csv")},
        headers=treasurer,
    )
    assert replay.status_code == 200, replay.text
    assert replay.json()["success_count"] == 0
    assert replay.json()["skipped_count"] == 1

    records = await client.get(
        "/api/v1/contributions/", params={"year": 2026}, headers=treasurer
    )
    assert len(records.json()) == 1
    record = records.json()[0]
    assert record["paid_amount"] == "40.00"
    assert record["status"] == "partial"
    payments = await client.get(
        f"/api/v1/contributions/{record['id']}/payments", headers=treasurer
    )
    assert len(payments.json()) == 1

    duplicate = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": str(people["member"]["profile"].id),
            "year": 2026,
            "expected_amount": "100.00",
        },
        headers=treasurer,
    )
    assert duplicate.status_code == 409


async def test_finance_journal_is_chronological_and_tenant_scoped(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)
    member = await _headers(client, people["member"], slug)
    profile_id = str(people["member"]["profile"].id)

    accounts = await client.get("/api/v1/contributions/accounts", headers=treasurer)
    cash = next(account for account in accounts.json() if account["kind"] == "cash")
    await client.put(
        f"/api/v1/contributions/accounts/{cash['id']}/opening-balance/2026",
        json={"amount": "100.00"},
        headers=treasurer,
    )

    contribution = await client.post(
        "/api/v1/contributions/",
        json={"membership_profile_id": profile_id, "year": 2026, "expected_amount": "100.00"},
        headers=treasurer,
    )
    assert contribution.status_code == 201, contribution.text
    payment = await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": contribution.json()["id"],
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
            "amount": "10.00",
            "spent_at": "2026-04-01T12:00:00Z",
            "description": "Postage",
            "payment_method": "bank_transfer",
        },
        headers=treasurer,
    )
    assert expense.status_code == 201, expense.text
    donation = await client.post(
        "/api/v1/contributions/receipt-declarations",
        json={
            "income_type": "donation",
            "source_name": "Local donor",
            "amount": "30.00",
            "received_at": "2026-05-01T12:00:00Z",
        },
        headers=treasurer,
    )
    assert donation.status_code == 201, donation.text
    await client.post(
        f"/api/v1/contributions/receipt-declarations/{donation.json()['id']}/submit",
        headers=treasurer,
    )
    await client.post(
        f"/api/v1/contributions/receipt-declarations/{donation.json()['id']}/process",
        json={"action": "validated"},
        headers=treasurer,
    )

    journal = await client.get(
        "/api/v1/contributions/journal/export", params={"year": 2026}, headers=treasurer
    )
    assert journal.status_code == 200, journal.text
    rows = list(csv.DictReader(io.StringIO(journal.text)))
    assert {row["type"] for row in rows} == {
        "opening_balance",
        "payment",
        "expense",
        "receipt_declaration",
    }
    payment_row = next(row for row in rows if row["type"] == "payment")
    assert payment_row["amount"] == "50.00"
    assert payment_row["reference"] == "2026-00001"
    assert payment_row["counterparty"].startswith(people["member"]["profile"].member_code)
    expense_row = next(row for row in rows if row["type"] == "expense")
    assert expense_row["amount"] == "10.00"
    assert expense_row["direction"] == "out"
    assert [row["date"] for row in rows] == sorted(row["date"] for row in rows)

    forbidden = await client.get(
        "/api/v1/contributions/journal/export", params={"year": 2026}, headers=member
    )
    assert forbidden.status_code == 403


async def test_raw_ledger_export_is_available_to_the_treasurer_and_safe(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    treasurer = await _headers(client, people["treasurer"], slug)
    member = await _headers(client, people["member"], slug)

    created = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": str(people["member"]["profile"].id),
            "year": 2026,
            "expected_amount": "100.00",
        },
        headers=treasurer,
    )
    assert created.status_code == 201, created.text

    raw = await client.get("/api/v1/contributions/export", headers=treasurer)
    assert raw.status_code == 200, raw.text
    assert "membership_profile_id" in raw.text
    assert (await client.get("/api/v1/contributions/export", headers=member)).status_code == 403

    report = await client.get(
        "/api/v1/contributions/report/export/xlsx",
        params={"year": 2026},
        headers=treasurer,
    )
    assert report.status_code == 200, report.text
    sheet = load_workbook(io.BytesIO(report.content)).active
    headers = [cell.value for cell in sheet[4]]
    assert not any("Sanction" in str(header) for header in headers)
    assert not any("Total" in str(header) for header in headers)

    whatsapp = await client.get(
        "/api/v1/contributions/report/export/whatsapp",
        params={"year": 2026},
        headers=treasurer,
    )
    assert whatsapp.status_code == 200
    assert "Sanctions" not in whatsapp.text
