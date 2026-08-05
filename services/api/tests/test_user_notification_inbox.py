from __future__ import annotations

import uuid

import pytest
from helpers import create_tenant_with_user, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.user_service import UserNotificationService
from app.modules.notifications.user_schemas import NotificationPreferencesUpdate


@pytest.mark.asyncio
async def test_user_inbox_is_tenant_isolated_and_outbox_is_idempotent(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    first = await create_tenant_with_user(db_session, f"inbox-a-{uuid.uuid4().hex[:6]}")
    second = await create_tenant_with_user(db_session, f"inbox-b-{uuid.uuid4().hex[:6]}")
    service = UserNotificationService(db_session)

    await service.enqueue(
        tenant_id=first["tenant"].id,
        event_type="finance.receipt_declared",
        recipients=[first["user"].id],
        category="finance",
        target_path="/finance",
        deduplication_key="inbox-isolation",
    )
    await db_session.commit()
    assert await service.process_outbox() == 1

    first_token = await login(client, first["user"].email, first["password"], first["tenant"].slug)
    second_token = await login(client, second["user"].email, second["password"], second["tenant"].slug)
    first_inbox = await client.get("/api/v1/notifications/inbox", headers={"Authorization": f"Bearer {first_token}"})
    second_inbox = await client.get("/api/v1/notifications/inbox", headers={"Authorization": f"Bearer {second_token}"})

    assert first_inbox.status_code == 200, first_inbox.text
    assert first_inbox.json()["unread_count"] == 1
    assert first_inbox.json()["items"][0]["event_type"] == "finance.receipt_declared"
    assert second_inbox.status_code == 200, second_inbox.text
    assert second_inbox.json()["items"] == []

    await service.enqueue(
        tenant_id=first["tenant"].id,
        event_type="finance.receipt_declared",
        recipients=[first["user"].id],
        category="finance",
        target_path="/finance",
        deduplication_key="inbox-isolation",
    )
    with pytest.raises(Exception):
        await db_session.commit()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_user_can_mark_only_own_inbox_item_as_read(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, f"inbox-read-{uuid.uuid4().hex[:6]}")
    service = UserNotificationService(db_session)
    await service.enqueue(
        tenant_id=context["tenant"].id,
        event_type="discipline.recorded",
        recipients=[context["user"].id],
        category="discipline",
        target_path="/discipline",
        deduplication_key="inbox-read",
        priority="high",
    )
    await db_session.commit()
    await service.process_outbox()
    token = await login(client, context["user"].email, context["password"], context["tenant"].slug)
    inbox = await client.get("/api/v1/notifications/inbox", headers={"Authorization": f"Bearer {token}"})
    notification_id = inbox.json()["items"][0]["id"]
    marked = await client.post(f"/api/v1/notifications/inbox/{notification_id}/read", headers={"Authorization": f"Bearer {token}"})
    assert marked.status_code == 204
    refreshed = await client.get("/api/v1/notifications/inbox", headers={"Authorization": f"Bearer {token}"})
    assert refreshed.json()["unread_count"] == 0


@pytest.mark.asyncio
async def test_notification_preferences_are_scoped_to_the_authenticated_device_profile(
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, f"inbox-preferences-{uuid.uuid4().hex[:6]}")
    service = UserNotificationService(db_session)
    await service.register_device(
        context["tenant"].id,
        context["user"].id,
        "browser-installation-001",
        "web",
        "test-agent",
    )

    updated = await service.update_preferences(
        context["tenant"].id,
        context["user"].id,
        NotificationPreferencesUpdate(
            push_enabled=True,
            finance_enabled=False,
            discipline_enabled=True,
            announcements_enabled=False,
            events_enabled=True,
        ),
    )
    current = await service.preferences(context["tenant"].id, context["user"].id)

    assert updated.finance_enabled is False
    assert current.finance_enabled is False
    assert current.announcements_enabled is False
    assert current.discipline_enabled is True
