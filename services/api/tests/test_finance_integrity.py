"""F0 treasury integrity: the payment ledger is the source of truth.

These tests protect the guarantees introduced by the treasury readiness audit:
- a contribution balance can only change through a recorded payment;
- a payment is idempotent and reversible, never silently deleted;
- a member with financial history cannot be deleted;
- every financial record uses the organization currency.
"""

import uuid

import pytest
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


async def _tenant_with_treasurer(db_session: AsyncSession, suffix: str) -> dict:
    admin = await create_tenant_with_user(db_session, suffix)
    treasurer = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"treasurer.{suffix}@test.org",
        password="TreasurerPass123!",
        display_name="Treasurer Integrity",
        role_code="treasurer",
        profile_type="staff",
    )
    member = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"member.{suffix}@test.org",
        password="MemberPass123!",
        display_name="Member Integrity",
        role_code="member",
        profile_type="member",
        member_code=f"INT-{suffix[:6].upper()}",
    )
    await db_session.commit()
    return {"admin": admin, "treasurer": treasurer, "member": member}


async def _headers_for(client: AsyncClient, person: dict, slug: str) -> dict:
    token = await login(client, person["user"].email, person["password"], slug)
    return {"Authorization": f"Bearer {token}"}


async def _create_contribution(
    client: AsyncClient,
    headers: dict,
    profile_id: str,
    *,
    expected: str = "100.00",
    paid: str = "0.00",
    status: str | None = None,
    currency: str | None = None,
    year: int = 2026,
) -> dict:
    payload: dict = {
        "membership_profile_id": profile_id,
        "year": year,
        "expected_amount": expected,
        "paid_amount": paid,
    }
    if status is not None:
        payload["status"] = status
    if currency is not None:
        payload["currency"] = currency
    response = await client.post(
        "/api/v1/contributions/", json=payload, headers=headers
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_opening_balance_is_backed_by_a_payment_and_status_is_derived(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant_with_treasurer(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    headers = await _headers_for(client, people["treasurer"], slug)

    record = await _create_contribution(
        client, headers, str(people["member"]["profile"].id), paid="40.00"
    )
    assert record["paid_amount"] == "40.00"
    assert record["balance"] == "60.00"
    assert record["status"] == "partial"

    payments = await client.get(
        f"/api/v1/contributions/{record['id']}/payments", headers=headers
    )
    assert payments.status_code == 200
    assert len(payments.json()) == 1
    assert payments.json()[0]["reference"] == "opening balance"
    assert payments.json()[0]["amount"] == "40.00"

    # A client can no longer overwrite the paid amount.
    patched = await client.patch(
        f"/api/v1/contributions/{record['id']}",
        json={"paid_amount": "100.00"},
        headers=headers,
    )
    assert patched.status_code == 422

    # A status that contradicts the ledger is refused at creation time.
    contradictory = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": str(people["member"]["profile"].id),
            "year": 2027,
            "expected_amount": "100.00",
            "paid_amount": "10.00",
            "status": "paid",
        },
        headers=headers,
    )
    assert contradictory.status_code == 422


async def test_payment_idempotency_prevents_double_recording(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant_with_treasurer(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    headers = await _headers_for(client, people["treasurer"], slug)
    record = await _create_contribution(
        client, headers, str(people["member"]["profile"].id)
    )

    payload = {
        "contribution_record_id": record["id"],
        "amount": "50.00",
        "payment_method": "cash",
        "idempotency_key": f"idem-{suffix}-0001",
    }
    first = await client.post("/api/v1/contributions/payments", json=payload, headers=headers)
    second = await client.post("/api/v1/contributions/payments", json=payload, headers=headers)
    assert first.status_code == 201, first.text
    assert second.status_code == 201, second.text
    assert first.json()["id"] == second.json()["id"]

    # Reusing the key for a different amount must not silently return the first payment.
    conflicting = await client.post(
        "/api/v1/contributions/payments",
        json={**payload, "amount": "60.00"},
        headers=headers,
    )
    assert conflicting.status_code == 409

    refreshed = await client.get(f"/api/v1/contributions/{record['id']}", headers=headers)
    assert refreshed.json()["paid_amount"] == "50.00"
    payments = await client.get(
        f"/api/v1/contributions/{record['id']}/payments", headers=headers
    )
    assert len(payments.json()) == 1


async def test_payment_reversal_restores_balance_and_keeps_history(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant_with_treasurer(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    headers = await _headers_for(client, people["treasurer"], slug)
    record = await _create_contribution(
        client, headers, str(people["member"]["profile"].id)
    )

    payment = await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": record["id"],
            "amount": "100.00",
            "payment_method": "bank_transfer",
        },
        headers=headers,
    )
    assert payment.status_code == 201, payment.text
    paid = await client.get(f"/api/v1/contributions/{record['id']}", headers=headers)
    assert paid.json()["status"] == "paid"
    assert paid.json()["balance"] == "0.00"

    reversed_payment = await client.post(
        f"/api/v1/contributions/payments/{payment.json()['id']}/reverse",
        json={"reason": "Payment recorded twice"},
        headers=headers,
    )
    assert reversed_payment.status_code == 200, reversed_payment.text
    assert reversed_payment.json()["reversed_at"] is not None
    assert reversed_payment.json()["reversal_reason"] == "Payment recorded twice"

    restored = await client.get(f"/api/v1/contributions/{record['id']}", headers=headers)
    assert restored.json()["paid_amount"] == "0.00"
    assert restored.json()["balance"] == "100.00"
    assert restored.json()["status"] == "pending"

    history = await client.get(
        f"/api/v1/contributions/{record['id']}/payments", headers=headers
    )
    assert len(history.json()) == 1
    assert history.json()[0]["reversed_at"] is not None

    again = await client.post(
        f"/api/v1/contributions/payments/{payment.json()['id']}/reverse",
        json={"reason": "Second attempt"},
        headers=headers,
    )
    assert again.status_code == 409


async def test_paid_contribution_cannot_be_deleted_but_an_empty_one_can(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant_with_treasurer(db_session, suffix)
    slug = people["admin"]["tenant"].slug
    headers = await _headers_for(client, people["treasurer"], slug)
    profile_id = str(people["member"]["profile"].id)

    paid_record = await _create_contribution(client, headers, profile_id, paid="100.00")
    admin_headers = await _headers_for(client, people["admin"], slug)
    refused = await client.delete(
        f"/api/v1/contributions/{paid_record['id']}", headers=admin_headers
    )
    assert refused.status_code == 409
    assert "reverse" in refused.json()["detail"].lower()
    still_listed = await client.get(
        "/api/v1/contributions/", params={"year": 2026}, headers=headers
    )
    assert [row["id"] for row in still_listed.json()] == [paid_record["id"]]

    unpaid_record = await _create_contribution(
        client, headers, profile_id, expected="25.00", year=2027
    )
    deleted = await client.delete(
        f"/api/v1/contributions/{unpaid_record['id']}", headers=admin_headers
    )
    assert deleted.status_code == 204


async def test_organization_currency_is_inherited_enforced_and_locked(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    people = await _tenant_with_treasurer(db_session, suffix)
    tenant = people["admin"]["tenant"]
    admin_headers = await _headers_for(client, people["admin"], tenant.slug)
    treasurer_headers = await _headers_for(client, people["treasurer"], tenant.slug)

    updated = await client.put(
        f"/api/v1/tenants/{tenant.id}/settings",
        json={"name": "Currency Association", "default_language": "fr", "currency": "CHF"},
        headers=admin_headers,
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["currency"] == "CHF"

    record = await _create_contribution(
        client, treasurer_headers, str(people["member"]["profile"].id), expected="120.00"
    )
    assert record["currency"] == "CHF"

    wrong_currency = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": str(people["member"]["profile"].id),
            "year": 2027,
            "expected_amount": "120.00",
            "currency": "EUR",
        },
        headers=treasurer_headers,
    )
    assert wrong_currency.status_code == 422

    expense = await client.post(
        "/api/v1/contributions/expenses",
        json={"category": "administration", "amount": "15.00", "description": "Postage"},
        headers=treasurer_headers,
    )
    assert expense.status_code == 201, expense.text
    assert expense.json()["currency"] == "CHF"

    budget = await client.get(
        "/api/v1/contributions/annual-budget", params={"year": 2026}, headers=treasurer_headers
    )
    assert budget.status_code == 200, budget.text
    assert budget.json()["currency"] == "CHF"

    locked = await client.put(
        f"/api/v1/tenants/{tenant.id}/settings",
        json={"name": "Currency Association", "default_language": "fr", "currency": "USD"},
        headers=admin_headers,
    )
    assert locked.status_code == 409


async def test_member_with_financial_history_cannot_be_deleted(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    suffix = uuid.uuid4().hex[:6]
    president_ctx = await create_tenant_with_user(
        db_session,
        f"integrity-{suffix}",
        role_code="president",
        profile_type="president",
    )
    treasurer = await create_user_for_tenant(
        db_session,
        tenant_id=president_ctx["tenant"].id,
        email=f"treasurer.delete.{suffix}@test.org",
        password="TreasurerPass123!",
        display_name="Treasurer Delete",
        role_code="treasurer",
        profile_type="staff",
    )
    await db_session.commit()
    slug = president_ctx["tenant"].slug
    president_headers = await _headers_for(client, president_ctx, slug)
    treasurer_headers = await _headers_for(client, treasurer, slug)

    created_profile = await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": f"DEL-{suffix[:6].upper()}",
            "first_name": "Financial",
            "last_name": "History",
            "display_name": "Financial History",
        },
        headers=president_headers,
    )
    assert created_profile.status_code == 201, created_profile.text
    profile_id = created_profile.json()["id"]

    contribution = await _create_contribution(
        client, treasurer_headers, profile_id, expected="80.00"
    )
    assert contribution["id"]

    refused = await client.delete(
        f"/api/v1/memberships/{profile_id}", headers=president_headers
    )
    assert refused.status_code == 409
    assert "history" in refused.json()["detail"].lower()
    still_there = await client.get(
        f"/api/v1/memberships/{profile_id}", headers=president_headers
    )
    assert still_there.status_code == 200

    empty_profile = await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": f"EMP-{suffix[:6].upper()}",
            "first_name": "Empty",
            "last_name": "Profile",
            "display_name": "Empty Profile",
        },
        headers=president_headers,
    )
    assert empty_profile.status_code == 201, empty_profile.text
    deleted = await client.delete(
        f"/api/v1/memberships/{empty_profile.json()['id']}", headers=president_headers
    )
    assert deleted.status_code == 204
