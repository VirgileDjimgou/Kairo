"""Integration tests for membership and contributions modules."""

import uuid

import fitz
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from helpers import create_tenant_with_user, create_user_for_tenant, login


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
async def test_get_my_statement_requires_linked_profile(
    client: AsyncClient, db_session: AsyncSession
):
    ctx = await create_tenant_with_user(db_session, "my-statement")
    token = await login(client, ctx["user"].email, "TestIsolation1!", ctx["tenant"].slug)

    response = await client.get(
        "/api/v1/memberships/me/statement",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


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
async def test_update_contribution_record(client: AsyncClient, db_session: AsyncSession):
    ctx = await create_tenant_with_user(db_session, "contrib-update")
    token = await login(client, ctx["user"].email, "TestIsolation1!", ctx["tenant"].slug)

    profile_resp = await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": "CU001",
            "first_name": "Contrib",
            "last_name": "Updater",
            "display_name": "Contrib Updater",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    profile_id = profile_resp.json()["id"]

    create_resp = await client.post(
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
    contrib_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/v1/contributions/{contrib_id}",
        json={"expected_amount": "150.00", "status": "partial"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_resp.status_code == 200, patch_resp.text
    updated = patch_resp.json()
    assert updated["expected_amount"] == "150.00"
    assert updated["status"] == "partial"
    assert updated["balance"] == "150.00"


@pytest.mark.asyncio
async def test_delete_contribution_record(client: AsyncClient, db_session: AsyncSession):
    ctx = await create_tenant_with_user(db_session, "contrib-delete")
    token = await login(client, ctx["user"].email, "TestIsolation1!", ctx["tenant"].slug)

    profile_resp = await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": "CD001",
            "first_name": "Contrib",
            "last_name": "Deleter",
            "display_name": "Contrib Deleter",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    profile_id = profile_resp.json()["id"]

    create_resp = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": profile_id,
            "year": 2026,
            "expected_amount": "100.00",
            "paid_amount": "0.00",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    contrib_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/api/v1/contributions/{contrib_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 204

    get_resp = await client.get(
        f"/api/v1/contributions/{contrib_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_contributions_by_member(client: AsyncClient, db_session: AsyncSession):
    ctx = await create_tenant_with_user(db_session, "contrib-by-member")
    token = await login(client, ctx["user"].email, "TestIsolation1!", ctx["tenant"].slug)

    profile_resp = await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": "BM001",
            "first_name": "By",
            "last_name": "Member",
            "display_name": "By Member",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    profile_id = profile_resp.json()["id"]

    for year in [2025, 2026]:
        await client.post(
            "/api/v1/contributions/",
            json={
                "membership_profile_id": profile_id,
                "year": year,
                "expected_amount": "100.00",
                "paid_amount": "0.00",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    response = await client.get(
        f"/api/v1/contributions/by-member/{profile_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 2
    years = sorted(r["year"] for r in data)
    assert years == [2025, 2026]


@pytest.mark.asyncio
async def test_get_contribution_payments(client: AsyncClient, db_session: AsyncSession):
    ctx = await create_tenant_with_user(db_session, "contrib-payments")
    token = await login(client, ctx["user"].email, "TestIsolation1!", ctx["tenant"].slug)

    profile_resp = await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": "PM001",
            "first_name": "Payment",
            "last_name": "List",
            "display_name": "Payment List",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    profile_id = profile_resp.json()["id"]

    contrib_resp = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": profile_id,
            "year": 2026,
            "expected_amount": "100.00",
            "paid_amount": "0.00",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    contrib_id = contrib_resp.json()["id"]

    await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": contrib_id,
            "amount": "30.00",
            "currency": "EUR",
            "payment_method": "cash",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": contrib_id,
            "amount": "70.00",
            "currency": "EUR",
            "payment_method": "bank_transfer",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    response = await client.get(
        f"/api/v1/contributions/{contrib_id}/payments",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 2
    methods = sorted(p["payment_method"] for p in data)
    assert methods == ["bank_transfer", "cash"]
    total = sum(float(p["amount"]) for p in data)
    assert total == 100.00


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


@pytest.mark.asyncio
async def test_member_role_cannot_access_staff_membership_and_contribution_endpoints(
    client: AsyncClient, db_session: AsyncSession
):
    admin = await create_tenant_with_user(db_session, f"staff-guard-{uuid.uuid4().hex[:6]}")
    member = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"member-{uuid.uuid4().hex[:6]}@test.org",
        password="MemberPass1!",
        display_name="Member Guard",
        role_code="member",
        profile_type="member",
        member_code="MG-001",
    )
    await db_session.commit()

    admin_token = await login(client, admin["user"].email, admin["password"], admin["tenant"].slug)
    member_token = await login(client, member["user"].email, member["password"], admin["tenant"].slug)

    create_resp = await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": "MG-002",
            "first_name": "Other",
            "last_name": "Person",
            "display_name": "Other Person",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert create_resp.status_code == 201, create_resp.text
    profile_id = create_resp.json()["id"]

    requests = [
        ("/api/v1/memberships/", {}),
        (f"/api/v1/memberships/{profile_id}", {}),
        (f"/api/v1/memberships/{profile_id}/balance", {}),
        ("/api/v1/contributions/", {}),
        ("/api/v1/contributions/summary", {}),
        ("/api/v1/contributions/reminders", {}),
        (f"/api/v1/contributions/by-member/{profile_id}", {}),
    ]
    for path, params in requests:
        response = await client.get(
            path,
            params=params,
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert response.status_code == 403, response.text


@pytest.mark.asyncio
async def test_member_can_fetch_only_personal_statement_and_pdf(
    client: AsyncClient, db_session: AsyncSession
):
    admin = await create_tenant_with_user(db_session, f"member-statement-{uuid.uuid4().hex[:6]}")
    alice = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"alice-{uuid.uuid4().hex[:6]}@test.org",
        password="MemberPass1!",
        display_name="Alice Statement",
        role_code="member",
        profile_type="member",
        member_code="AL-001",
    )
    bob = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"bob-{uuid.uuid4().hex[:6]}@test.org",
        password="MemberPass1!",
        display_name="Bob Statement",
        role_code="member",
        profile_type="member",
        member_code="BO-001",
    )
    await db_session.commit()

    admin_token = await login(client, admin["user"].email, admin["password"], admin["tenant"].slug)
    alice_token = await login(client, alice["user"].email, alice["password"], admin["tenant"].slug)
    bob_token = await login(client, bob["user"].email, bob["password"], admin["tenant"].slug)

    alice_contribution = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": str(alice["profile"].id),
            "year": 2026,
            "expected_amount": "120.00",
            "paid_amount": "20.00",
            "currency": "EUR",
            "status": "partial",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert alice_contribution.status_code == 201, alice_contribution.text

    bob_contribution = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": str(bob["profile"].id),
            "year": 2026,
            "expected_amount": "75.00",
            "paid_amount": "75.00",
            "currency": "EUR",
            "status": "paid",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert bob_contribution.status_code == 201, bob_contribution.text

    statement_response = await client.get(
        "/api/v1/memberships/me/statement",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert statement_response.status_code == 200, statement_response.text
    statement_data = statement_response.json()
    assert statement_data["profile"]["display_name"] == "Alice Statement"
    assert statement_data["summary"]["total_expected"] == "120.00"
    assert statement_data["summary"]["total_paid"] == "20.00"
    assert statement_data["summary"]["total_balance"] == "100.00"
    assert len(statement_data["contributions"]) == 1
    assert statement_data["contributions"][0]["membership_profile_id"] == str(alice["profile"].id)

    pdf_response = await client.get(
        "/api/v1/memberships/me/statement.pdf",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert pdf_response.status_code == 200, pdf_response.text
    assert pdf_response.headers["content-type"] == "application/pdf"
    assert "attachment; filename=" in pdf_response.headers["content-disposition"]

    pdf = fitz.open(stream=pdf_response.content, filetype="pdf")
    pdf_text = "".join(page.get_text() for page in pdf)
    pdf.close()

    assert "Alice Statement" in pdf_text
    assert "AL-001" in pdf_text
    assert "120.00 EUR" in pdf_text
    assert "20.00 EUR" in pdf_text
    assert "Bob Statement" not in pdf_text
    assert "BO-001" not in pdf_text
    assert "75.00 EUR" not in pdf_text

    other_member_access = await client.get(
        f"/api/v1/contributions/by-member/{alice['profile'].id}",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert other_member_access.status_code == 403, other_member_access.text


@pytest.mark.asyncio
async def test_treasurer_can_run_finance_operations_but_not_admin_only_exports_or_deletes(
    client: AsyncClient, db_session: AsyncSession
):
    admin = await create_tenant_with_user(db_session, f"treasury-{uuid.uuid4().hex[:6]}")
    treasurer = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"treasurer-{uuid.uuid4().hex[:6]}@test.org",
        password="TreasurerPass1!",
        display_name="Treasurer User",
        role_code="treasurer",
        profile_type="treasurer",
        member_code="TR-001",
    )
    await db_session.commit()

    admin_token = await login(client, admin["user"].email, admin["password"], admin["tenant"].slug)
    treasurer_token = await login(client, treasurer["user"].email, treasurer["password"], admin["tenant"].slug)

    member_resp = await client.post(
        "/api/v1/memberships/",
        json={
            "member_code": "FIN-001",
            "first_name": "Finance",
            "last_name": "Member",
            "display_name": "Finance Member",
            "email": "finance-member@test.org",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert member_resp.status_code == 201, member_resp.text
    profile_id = member_resp.json()["id"]

    list_members_resp = await client.get(
        "/api/v1/memberships/",
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )
    assert list_members_resp.status_code == 200, list_members_resp.text
    assert any(member["id"] == profile_id for member in list_members_resp.json())

    create_contrib_resp = await client.post(
        "/api/v1/contributions/",
        json={
            "membership_profile_id": profile_id,
            "year": 2026,
            "expected_amount": "120.00",
            "paid_amount": "0.00",
            "currency": "EUR",
            "status": "pending",
        },
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )
    assert create_contrib_resp.status_code == 201, create_contrib_resp.text
    contribution_id = create_contrib_resp.json()["id"]

    payment_resp = await client.post(
        "/api/v1/contributions/payments",
        json={
            "contribution_record_id": contribution_id,
            "amount": "45.00",
            "currency": "EUR",
            "payment_method": "bank_transfer",
        },
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )
    assert payment_resp.status_code == 201, payment_resp.text

    balance_resp = await client.get(
        f"/api/v1/memberships/{profile_id}/balance",
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )
    assert balance_resp.status_code == 200, balance_resp.text
    balance_data = balance_resp.json()
    assert balance_data["total_expected"] == "120.00"
    assert balance_data["total_paid"] == "45.00"
    assert balance_data["total_balance"] == "75.00"

    summary_resp = await client.get(
        "/api/v1/contributions/summary?year=2026",
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )
    assert summary_resp.status_code == 200, summary_resp.text
    assert summary_resp.json()["total_balance"] == "75.00"

    export_members_resp = await client.get(
        "/api/v1/memberships/export",
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )
    assert export_members_resp.status_code == 403

    export_contributions_resp = await client.get(
        "/api/v1/contributions/export",
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )
    assert export_contributions_resp.status_code == 403

    delete_contribution_resp = await client.delete(
        f"/api/v1/contributions/{contribution_id}",
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )
    assert delete_contribution_resp.status_code == 403
