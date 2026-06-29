from __future__ import annotations

import csv
import io
import uuid as _uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from helpers import create_tenant_with_user, login

pytestmark = pytest.mark.asyncio


async def _create_member_profile(
    client: AsyncClient,
    token: str,
    *,
    member_code: str,
    first_name: str,
    last_name: str,
    display_name: str,
) -> dict:
    response = await client.post(
        "/api/v1/memberships/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "member_code": member_code,
            "first_name": first_name,
            "last_name": last_name,
            "display_name": display_name,
            "email": f"{member_code}@example.org",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _create_contribution(
    client: AsyncClient,
    token: str,
    *,
    membership_profile_id: str,
    year: int = 2026,
) -> dict:
    response = await client.post(
        "/api/v1/contributions/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "membership_profile_id": membership_profile_id,
            "year": year,
            "expected_amount": "100.00",
            "paid_amount": "25.00",
            "currency": "EUR",
            "status": "pending",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _update_settings(client: AsyncClient, token: str, tenant_id: str) -> dict:
    response = await client.put(
        f"/api/v1/tenants/{tenant_id}/settings",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Audit Friendly Org",
            "branding": {"primary_color": "#123456", "logo_url": "https://example.org/logo.png"},
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


async def test_audit_trail_logs_sensitive_actions_and_filters_by_entity(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    data = await create_tenant_with_user(db_session, f"audit-{_uuid.uuid4().hex[:6]}")
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    member = await _create_member_profile(
        client,
        token,
        member_code=f"MEM-{_uuid.uuid4().hex[:6]}",
        first_name="Ada",
        last_name="Lovelace",
        display_name="Ada Lovelace",
    )
    contribution = await _create_contribution(
        client,
        token,
        membership_profile_id=member["id"],
    )
    await _update_settings(client, token, str(data["tenant"].id))

    resp = await client.get(
        "/api/v1/admin/audit/events",
        headers={"Authorization": f"Bearer {token}"},
        params={"limit": 20},
    )
    assert resp.status_code == 200, resp.text
    events = resp.json()
    assert len(events) >= 3

    entity_types = {event["entity_type"] for event in events}
    assert {"membership_profile", "contribution_record", "tenant_settings"}.issubset(entity_types)

    filtered = await client.get(
        "/api/v1/admin/audit/events",
        headers={"Authorization": f"Bearer {token}"},
        params={"action": "create", "entity_type": "membership_profile"},
    )
    assert filtered.status_code == 200, filtered.text
    filtered_events = filtered.json()
    assert len(filtered_events) == 1
    assert filtered_events[0]["entity_id"] == member["id"]
    assert filtered_events[0]["details"]["member_code"] == member["member_code"]

    export_resp = await client.get(
        "/api/v1/admin/audit/events/export",
        headers={"Authorization": f"Bearer {token}"},
        params={"format": "csv"},
    )
    assert export_resp.status_code == 200, export_resp.text
    assert export_resp.headers["content-type"].startswith("text/csv")

    reader = csv.DictReader(io.StringIO(export_resp.text))
    rows = list(reader)
    assert len(rows) >= 3
    assert any(row["entity_type"] == "contribution_record" for row in rows)
    assert any(row["entity_id"] == contribution["id"] for row in rows)


async def test_audit_trail_is_tenant_scoped(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    tenant_a = await create_tenant_with_user(db_session, f"audit-a-{_uuid.uuid4().hex[:6]}")
    token_a = await login(client, tenant_a["user"].email, tenant_a["password"], tenant_slug=tenant_a["tenant"].slug)
    await _create_member_profile(
        client,
        token_a,
        member_code=f"A-{_uuid.uuid4().hex[:6]}",
        first_name="Tenant",
        last_name="A",
        display_name="Tenant A Member",
    )

    tenant_b = await create_tenant_with_user(db_session, f"audit-b-{_uuid.uuid4().hex[:6]}")
    token_b = await login(client, tenant_b["user"].email, tenant_b["password"], tenant_slug=tenant_b["tenant"].slug)

    resp = await client.get(
        "/api/v1/admin/audit/events",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json() == []

