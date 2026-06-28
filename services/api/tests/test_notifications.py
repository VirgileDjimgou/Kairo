"""Sprint 14 integration tests: multi-channel notification placeholders."""

from __future__ import annotations

import uuid as _uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from helpers import create_tenant_with_user, login
from test_events_announcements import _create_linked_member


@pytest.mark.asyncio
async def test_admin_can_list_notification_channels(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"notif-list-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)

    response = await client.get(
        "/api/v1/notifications/channels",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    channels = response.json()
    assert [channel["channel"] for channel in channels] == ["email", "telegram", "whatsapp"]
    assert all(channel["simulation_only"] is True for channel in channels)


@pytest.mark.asyncio
async def test_non_admin_cannot_list_notification_channels(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"notif-lock-{_uuid.uuid4().hex[:6]}")
    member = await _create_linked_member(
        db_session,
        tenant_id=ctx["tenant"].id,
        email=f"member-notif-{_uuid.uuid4().hex[:6]}@test.org",
        password="NotifMember1!",
        member_code="NT-001",
        display_name="Notification Member",
    )
    token = await login(client, member["user"].email, member["password"], tenant_slug=ctx["tenant"].slug)

    response = await client.get(
        "/api/v1/notifications/channels",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_send_simulated_multi_channel_notification(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"notif-send-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)

    response = await client.post(
        "/api/v1/notifications/test",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "channels": ["email", "telegram", "email"],
            "recipient": "ops@example.org",
            "subject": "Kairo test",
            "body": "This is a dry-run notification.",
        },
    )
    assert response.status_code == 200, response.text
    results = response.json()["results"]
    assert [item["channel"] for item in results] == ["email", "telegram"]
    assert all(item["status"] == "simulated" for item in results)
    assert all(item["delivered"] is False for item in results)
    assert all(item["simulation_only"] is True for item in results)


@pytest.mark.asyncio
async def test_unknown_notification_channel_is_rejected(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"notif-err-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)

    response = await client.post(
        "/api/v1/notifications/test",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "channels": ["pagerduty"],
            "recipient": "ops@example.org",
            "body": "Unsupported channel test",
        },
    )
    assert response.status_code == 400
    assert "Unknown notification channel" in response.json()["detail"]
