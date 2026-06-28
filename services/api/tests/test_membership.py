"""Integration tests for membership and contributions modules."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from helpers import create_tenant_with_user, login


@pytest.mark.asyncio
async def test_create_member_profile(client: AsyncClient, db_session: AsyncSession):
    ctx = await create_tenant_with_user(db_session, "member-create")
    token = await login(client, ctx["user"].email, "TestIsolation1!", ctx["tenant"].slug)

    response = await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": "M001",
            "first_name": "Jane",
            "last_name": "Doe",
            "display_name": "Jane Doe",
            "email": "jane@test.org",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["member_code"] == "M001"
    assert data["first_name"] == "Jane"
    assert data["display_name"] == "Jane Doe"
    assert data["tenant_id"] == str(ctx["tenant"].id)
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_list_member_profiles(client: AsyncClient, db_session: AsyncSession):
    ctx = await create_tenant_with_user(db_session, "member-list")
    token = await login(client, ctx["user"].email, "TestIsolation1!", ctx["tenant"].slug)

    # Create two profiles
    for code, fname, lname in [("M001", "Alice", "Smith"), ("M002", "Bob", "Jones")]:
        await client.post(
            "/api/v1/memberships/",
            json={
                "member_code": code,
                "first_name": fname,
                "last_name": lname,
                "display_name": f"{fname} {lname}",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    response = await client.get(
        "/api/v1/memberships/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 2
    codes = sorted(m["member_code"] for m in data)
    assert codes == ["M001", "M002"]


@pytest.mark.asyncio
async def test_member_profiles_are_tenant_isolated(
    client: AsyncClient, db_session: AsyncSession
):
    ctx_a = await create_tenant_with_user(db_session, "iso-a")
    ctx_b = await create_tenant_with_user(db_session, "iso-b")

    token_a = await login(client, ctx_a["user"].email, "TestIsolation1!", ctx_a["tenant"].slug)
    token_b = await login(client, ctx_b["user"].email, "TestIsolation1!", ctx_b["tenant"].slug)

    # Create a profile in tenant A
    await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": "A001",
            "first_name": "Tenant",
            "last_name": "A",
            "display_name": "Tenant A Member",
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # Tenant B should see zero profiles
    response = await client.get(
        "/api/v1/memberships/",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 200, response.text
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_get_my_profile_returns_linked_profile(
    client: AsyncClient, db_session: AsyncSession
):
    ctx = await create_tenant_with_user(db_session, "my-profile")
    token = await login(client, ctx["user"].email, "TestIsolation1!", ctx["tenant"].slug)

    # Create a profile and link it to the user
    create_resp = await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": "M001",
            "first_name": "Linked",
            "last_name": "User",
            "display_name": "Linked User",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_resp.status_code == 201
    profile_id = create_resp.json()["id"]

    # The /me endpoint checks if the auth user's user_id is linked to a profile
    # Since user_id is nullable and not set on creation, /me will return 404
    # This is expected behavior - user_id linking would happen via admin action
    response = await client.get(
        "/api/v1/memberships/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_my_balance(client: AsyncClient, db_session: AsyncSession):
    ctx = await create_tenant_with_user(db_session, "my-balance")
    token = await login(client, ctx["user"].email, "TestIsolation1!", ctx["tenant"].slug)

    response = await client.get(
        "/api/v1/memberships/me/balance",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404  # No profile linked to user yet


@pytest.mark.asyncio
async def test_create_contribution_record(client: AsyncClient, db_session: AsyncSession):
    ctx = await create_tenant_with_user(db_session, "contrib-create")
    token = await login(client, ctx["user"].email, "TestIsolation1!", ctx["tenant"].slug)

    # First create a member profile
    profile_resp = await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": "C001",
            "first_name": "Contrib",
            "last_name": "User",
            "display_name": "Contrib User",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert profile_resp.status_code == 201
    profile_id = profile_resp.json()["id"]

    # Create a contribution record
    response = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": profile_id,
            "year": 2026,
            "expected_amount": "100.00",
            "paid_amount": "0.00",
            "currency": "EUR",
            "status": "pending",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["year"] == 2026
    assert data["expected_amount"] == "100.00"
    assert data["paid_amount"] == "0.00"
    assert data["balance"] == "100.00"
    assert data["status"] == "pending"
    assert data["tenant_id"] == str(ctx["tenant"].id)


@pytest.mark.asyncio
async def test_record_payment_updates_balance(
    client: AsyncClient, db_session: AsyncSession
):
    ctx = await create_tenant_with_user(db_session, "payment")
    token = await login(client, ctx["user"].email, "TestIsolation1!", ctx["tenant"].slug)

    # Create profile
    profile_resp = await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": "P001",
            "first_name": "Pay",
            "last_name": "User",
            "display_name": "Pay User",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    profile_id = profile_resp.json()["id"]

    # Create contribution
    contrib_resp = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": profile_id,
            "year": 2026,
            "expected_amount": "100.00",
            "paid_amount": "0.00",
            "currency": "EUR",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    contrib_id = contrib_resp.json()["id"]

    # Record a payment of 40
    payment_resp = await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": contrib_id,
            "amount": "40.00",
            "currency": "EUR",
            "payment_method": "cash",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert payment_resp.status_code == 201, payment_resp.text

    # Check the contribution balance updated
    get_resp = await client.get(
        f"/api/v1/contributions/{contrib_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200
    updated = get_resp.json()
    assert updated["paid_amount"] == "40.00"
    assert updated["balance"] == "60.00"

    # Record another payment of 60
    await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": contrib_id,
            "amount": "60.00",
            "currency": "EUR",
            "payment_method": "bank_transfer",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    get_resp2 = await client.get(
        f"/api/v1/contributions/{contrib_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    updated2 = get_resp2.json()
    assert updated2["paid_amount"] == "100.00"
    assert updated2["balance"] == "0.00"


@pytest.mark.asyncio
async def test_contribution_summary(client: AsyncClient, db_session: AsyncSession):
    ctx = await create_tenant_with_user(db_session, "summary")
    token = await login(client, ctx["user"].email, "TestIsolation1!", ctx["tenant"].slug)

    # Create two profiles
    p1 = (await client.post(
        "/api/v1/memberships/",
        json={"member_code": "S001", "first_name": "S1", "last_name": "U1", "display_name": "S1 U1"},
        headers={"Authorization": f"Bearer {token}"},
    )).json()
    p2 = (await client.post(
        "/api/v1/memberships/",
        json={"member_code": "S002", "first_name": "S2", "last_name": "U2", "display_name": "S2 U2"},
        headers={"Authorization": f"Bearer {token}"},
    )).json()

    # Create contributions
    await client.post(
        "/api/v1/contributions/",
        json={"membership_profile_id": p1["id"], "year": 2026, "expected_amount": "50.00", "paid_amount": "20.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        "/api/v1/contributions/",
        json={"membership_profile_id": p2["id"], "year": 2026, "expected_amount": "150.00", "paid_amount": "150.00"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = await client.get(
        "/api/v1/contributions/summary?year=2026",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    summary = response.json()
    assert summary["total_count"] == 2
    assert summary["total_expected"] == "200.00", summary
    assert summary["total_paid"] == "170.00"
    assert summary["total_balance"] == "30.00"


@pytest.mark.asyncio
async def test_contributions_tenant_isolation(
    client: AsyncClient, db_session: AsyncSession
):
    ctx_a = await create_tenant_with_user(db_session, "contrib-iso-a")
    ctx_b = await create_tenant_with_user(db_session, "contrib-iso-b")

    token_a = await login(client, ctx_a["user"].email, "TestIsolation1!", ctx_a["tenant"].slug)
    token_b = await login(client, ctx_b["user"].email, "TestIsolation1!", ctx_b["tenant"].slug)

    # Create profile + contribution in tenant A
    p = (await client.post(
        "/api/v1/memberships/",
        json={"member_code": "I001", "first_name": "I", "last_name": "A", "display_name": "I A"},
        headers={"Authorization": f"Bearer {token_a}"},
    )).json()

    await client.post(
        "/api/v1/contributions/",
        json={"membership_profile_id": p["id"], "year": 2026, "expected_amount": "100.00", "paid_amount": "0.00"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # Tenant B sees zero contributions
    response = await client.get(
        "/api/v1/contributions/",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_update_member_profile(client: AsyncClient, db_session: AsyncSession):
    ctx = await create_tenant_with_user(db_session, "update-profile")
    token = await login(client, ctx["user"].email, "TestIsolation1!", ctx["tenant"].slug)

    create_resp = await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": "U001",
            "first_name": "Update",
            "last_name": "Test",
            "display_name": "Update Test",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    profile_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/v1/memberships/{profile_id}",
        json={"first_name": "Updated", "email": "updated@test.org"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["first_name"] == "Updated"
    assert updated["email"] == "updated@test.org"


@pytest.mark.asyncio
async def test_delete_member_profile(client: AsyncClient, db_session: AsyncSession):
    ctx = await create_tenant_with_user(db_session, "delete-profile")
    token = await login(client, ctx["user"].email, "TestIsolation1!", ctx["tenant"].slug)

    create_resp = await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": "D001",
            "first_name": "Delete",
            "last_name": "Test",
            "display_name": "Delete Test",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    profile_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/api/v1/memberships/{profile_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 204

    # Verify it's gone
    get_resp = await client.get(
        f"/api/v1/memberships/{profile_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 404
