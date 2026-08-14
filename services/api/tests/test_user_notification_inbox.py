from __future__ import annotations

import uuid

import pytest
from helpers import create_tenant_with_user, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.user_service import UserNotificationService
from app.modules.notifications.user_schemas import NotificationPreferencesUpdate
from app.modules.notifications.user_models import FirebasePushSubscription
from sqlalchemy import select


@pytest.mark.asyncio
async def test_user_inbox_is_tenant_isolated_and_outbox_is_idempotent(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    first = await create_tenant_with_user(db_session, f"inbox-a-{uuid.uuid4().hex[:6]}")
    second = await create_tenant_with_user(db_session, f"inbox-b-{uuid.uuid4().hex[:6]}")
    service = UserNotificationService(db_session)

    # The outbox worker is intentionally global. Drain any events left by
    # preceding integration scenarios before asserting this event's count.
    await service.process_outbox()

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
    await service.register_device(
        context["tenant"].id,
        context["user"].id,
        "android-installation-002",
        "android",
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

    profiles = await service._profiles(context["tenant"].id, context["user"].id)
    assert len(profiles) == 2
    assert all(profile.push_enabled for profile in profiles)
    assert all('"finance_enabled": false' in profile.preferences_json for profile in profiles)


@pytest.mark.asyncio
async def test_firebase_push_token_is_registered_only_for_the_authenticated_tenant(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    first = await create_tenant_with_user(db_session, f"fcm-a-{uuid.uuid4().hex[:6]}")
    second = await create_tenant_with_user(db_session, f"fcm-b-{uuid.uuid4().hex[:6]}")
    token = "f" * 64
    installation_id = "android-installation-0001"

    first_access_token = await login(client, first["user"].email, first["password"], first["tenant"].slug)
    response = await client.post(
        "/api/v1/notifications/mobile-push-tokens",
        headers={"Authorization": f"Bearer {first_access_token}"},
        json={"installation_id": installation_id, "fcm_token": token},
    )
    assert response.status_code == 204, response.text

    subscriptions = list((await db_session.execute(select(FirebasePushSubscription))).scalars())
    assert len(subscriptions) == 1
    assert subscriptions[0].tenant_id == first["tenant"].id
    assert subscriptions[0].recipient_user_id == first["user"].id

    second_access_token = await login(client, second["user"].email, second["password"], second["tenant"].slug)
    response = await client.post(
        "/api/v1/notifications/mobile-push-tokens",
        headers={"Authorization": f"Bearer {second_access_token}"},
        json={"installation_id": installation_id, "fcm_token": token},
    )
    assert response.status_code == 204, response.text
    subscriptions = list((await db_session.execute(select(FirebasePushSubscription))).scalars())
    assert len(subscriptions) == 2
    assert {item.tenant_id for item in subscriptions} == {first["tenant"].id, second["tenant"].id}
    assert {item.recipient_user_id for item in subscriptions} == {first["user"].id, second["user"].id}
