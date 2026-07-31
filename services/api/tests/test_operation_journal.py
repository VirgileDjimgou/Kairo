from __future__ import annotations

import uuid as _uuid

import pytest
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


async def test_operation_journal_is_limited_to_president_and_secretary(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    data = await create_tenant_with_user(db_session, f"journal-{_uuid.uuid4().hex[:6]}")
    secretary = await create_user_for_tenant(
        db_session,
        tenant_id=data["tenant"].id,
        email=f"secretary-{_uuid.uuid4().hex[:6]}@test.org",
        password="SecretaryPass123!",
        display_name="Secretary",
        role_code="secretary_general",
        profile_type="staff",
    )
    treasurer = await create_user_for_tenant(
        db_session,
        tenant_id=data["tenant"].id,
        email=f"treasurer-{_uuid.uuid4().hex[:6]}@test.org",
        password="TreasurerPass123!",
        display_name="Treasurer",
        role_code="treasurer",
        profile_type="staff",
    )
    secretary_token = await login(client, secretary["user"].email, secretary["password"], data["tenant"].slug)
    treasurer_token = await login(client, treasurer["user"].email, treasurer["password"], data["tenant"].slug)

    failure = await client.post(
        "/api/v1/admin/audit/operation-journal/failures",
        headers={"Authorization": f"Bearer {treasurer_token}"},
        json={"method": "POST", "path": "/api/v1/memberships/", "status_code": 422},
    )
    assert failure.status_code == 204, failure.text

    allowed = await client.get(
        "/api/v1/admin/audit/operation-journal",
        headers={"Authorization": f"Bearer {secretary_token}"},
    )
    assert allowed.status_code == 200, allowed.text
    failed_event = next(row for row in allowed.json() if row["action"] == "operation_failed")
    assert failed_event["actor"]["display_name"] == "Treasurer"
    assert failed_event["actor"]["email"] == treasurer["user"].email
    assert failed_event["actor"]["roles"] == ["treasurer"]

    denied = await client.get(
        "/api/v1/admin/audit/operation-journal",
        headers={"Authorization": f"Bearer {treasurer_token}"},
    )
    assert denied.status_code == 403, denied.text
