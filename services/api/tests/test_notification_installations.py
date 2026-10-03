"""Browser installation normalization, isolation, rotation and retry telemetry."""

from __future__ import annotations

import json
import uuid

import pytest
import pytest_asyncio
from fakes import FakeFirebasePushProvider, FakeWebPushProvider
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.user_models import (
    FirebasePushSubscription,
    NotificationDevice,
    NotificationDeviceProfile,
    NotificationOutboxEvent,
    UserNotification,
    WebPushSubscription,
)
from app.modules.notifications.user_service import UserNotificationService

WEB_ENDPOINT = "https://push.example.org/installations/web"
WEB_ENDPOINT_TWO = "https://push.example.org/installations/web-two"
FCM_TOKEN_ONE = "a" * 64
FCM_TOKEN_TWO = "b" * 64
INSTALLATION = "installation-normalized-0001"
INSTALLATION_TWO = "installation-normalized-0002"


@pytest_asyncio.fixture(autouse=True)
async def _clean_notification_tables(db_session: AsyncSession):
    """Keep this file hermetic: the shared test connection keeps committed rows."""
    yield
    for model in (
        FirebasePushSubscription,
        WebPushSubscription,
        NotificationDeviceProfile,
        NotificationOutboxEvent,
        UserNotification,
    ):
        await db_session.execute(delete(model))
    await db_session.execute(delete(NotificationDevice))
    await db_session.commit()


async def _register_web_installation(
    service: UserNotificationService,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    *,
    installation_id: str = INSTALLATION,
    endpoint: str = WEB_ENDPOINT,
) -> NotificationDevice:
    return await service.register_device(
        tenant_id,
        user_id,
        installation_id,
        "Linux",
        "test-agent",
        "Chrome",
        {"language": "fr", "display_mode": "standalone"},
    )


@pytest.mark.asyncio
async def test_registration_normalizes_installation_metadata(db_session: AsyncSession) -> None:
    context = await create_tenant_with_user(db_session, "install-meta")
    service = UserNotificationService(db_session)

    device = await _register_web_installation(
        service, context["tenant"].id, context["user"].id
    )

    assert device.browser == "Chrome"
    assert device.platform == "Linux"
    assert device.status == "active"
    assert device.revoked_at is None
    assert device.updated_at is not None
    metadata = json.loads(device.device_metadata_json)
    assert metadata["language"] == "fr"
    assert metadata["display_mode"] == "standalone"


@pytest.mark.asyncio
async def test_multiple_installations_are_independent(db_session: AsyncSession) -> None:
    context = await create_tenant_with_user(db_session, "install-multi")
    service = UserNotificationService(db_session)
    tenant_id = context["tenant"].id
    user_id = context["user"].id

    await _register_web_installation(service, tenant_id, user_id)
    await service.save_subscription(
        tenant_id, user_id, INSTALLATION, "Linux", "test-agent", WEB_ENDPOINT, "p256dh-one", "auth-one"
    )
    await _register_web_installation(
        service, tenant_id, user_id, installation_id=INSTALLATION_TWO, endpoint=WEB_ENDPOINT_TWO
    )
    await service.save_subscription(
        tenant_id, user_id, INSTALLATION_TWO, "Linux", "test-agent", WEB_ENDPOINT_TWO, "p256dh-two", "auth-two"
    )

    revoked = await service.revoke_device(tenant_id, user_id, INSTALLATION)
    assert revoked == (1, 1, 0)

    first_device = await db_session.scalar(
        select(NotificationDevice).where(
            NotificationDevice.tenant_id == tenant_id,
            NotificationDevice.installation_id == INSTALLATION,
        )
    )
    second_device = await db_session.scalar(
        select(NotificationDevice).where(
            NotificationDevice.tenant_id == tenant_id,
            NotificationDevice.installation_id == INSTALLATION_TWO,
        )
    )
    assert first_device is not None and first_device.status == "revoked"
    assert first_device.revoked_at is not None
    assert second_device is not None and second_device.status == "active"

    second_subscription = await db_session.scalar(
        select(WebPushSubscription).where(WebPushSubscription.device_id == second_device.id)
    )
    assert second_subscription is not None
    assert second_subscription.disabled_at is None
    assert second_subscription.provider == "web_push"


@pytest.mark.asyncio
async def test_shared_installation_keeps_other_profile_binding(db_session: AsyncSession) -> None:
    context = await create_tenant_with_user(db_session, "install-shared")
    service = UserNotificationService(db_session)
    tenant_id = context["tenant"].id

    # Two profiles of the same tenant share one browser installation.
    second = await create_user_for_tenant(
        db_session,
        tenant_id=tenant_id,
        email="install-shared-second@test.org",
        password="TestIsolation1!",
        display_name="Second Profile",
    )
    await service.register_device(tenant_id, context["user"].id, INSTALLATION, "web", "test-agent")
    await service.save_subscription(
        tenant_id, context["user"].id, INSTALLATION, "web", "test-agent", WEB_ENDPOINT, "p256dh", "auth"
    )
    await service.register_device(tenant_id, second["user"].id, INSTALLATION, "web", "test-agent")

    revoked = await service.revoke_device(tenant_id, context["user"].id, INSTALLATION)
    assert revoked == (1, 0, 0)

    device = await db_session.scalar(
        select(NotificationDevice).where(NotificationDevice.installation_id == INSTALLATION)
    )
    assert device is not None and device.status == "active"
    subscription = await db_session.scalar(
        select(WebPushSubscription).where(WebPushSubscription.device_id == device.id)
    )
    assert subscription is not None and subscription.disabled_at is None
    remaining_profile = await db_session.scalar(
        select(NotificationDeviceProfile).where(
            NotificationDeviceProfile.device_id == device.id,
            NotificationDeviceProfile.user_id == second["user"].id,
        )
    )
    assert remaining_profile is not None and remaining_profile.revoked_at is None


@pytest.mark.asyncio
async def test_installations_and_tokens_are_tenant_scoped(db_session: AsyncSession) -> None:
    tenant_a = await create_tenant_with_user(db_session, "install-tenant-a")
    tenant_b = await create_tenant_with_user(db_session, "install-tenant-b")
    service = UserNotificationService(db_session)

    for context in (tenant_a, tenant_b):
        await service.save_firebase_subscription(
            context["tenant"].id,
            context["user"].id,
            INSTALLATION,
            "test-agent",
            FCM_TOKEN_ONE,
            "web",
            "Chrome",
            {"language": "fr"},
        )

    devices = list(
        (
            await db_session.execute(
                select(NotificationDevice).where(NotificationDevice.installation_id == INSTALLATION)
            )
        ).scalars()
    )
    assert len(devices) == 2
    assert {device.tenant_id for device in devices} == {tenant_a["tenant"].id, tenant_b["tenant"].id}

    revoked = await service.revoke_device(
        tenant_a["tenant"].id, tenant_a["user"].id, INSTALLATION
    )
    assert revoked == (1, 0, 1)

    tenant_b_token = await db_session.scalar(
        select(FirebasePushSubscription).where(
            FirebasePushSubscription.tenant_id == tenant_b["tenant"].id
        )
    )
    assert tenant_b_token is not None and tenant_b_token.disabled_at is None
    tenant_a_token = await db_session.scalar(
        select(FirebasePushSubscription).where(
            FirebasePushSubscription.tenant_id == tenant_a["tenant"].id
        )
    )
    assert tenant_a_token is not None and tenant_a_token.disabled_at is not None


@pytest.mark.asyncio
async def test_firebase_token_rotation_disables_obsolete_tokens(db_session: AsyncSession) -> None:
    context = await create_tenant_with_user(db_session, "install-rotation")
    service = UserNotificationService(db_session)
    tenant_id = context["tenant"].id
    user_id = context["user"].id

    await service.save_firebase_subscription(
        tenant_id, user_id, INSTALLATION, "test-agent", FCM_TOKEN_ONE, "web", "Chrome"
    )
    await service.save_firebase_subscription(
        tenant_id, user_id, INSTALLATION, "test-agent", FCM_TOKEN_TWO, "web", "Chrome"
    )
    # Re-registering the same current token must not create a duplicate.
    await service.save_firebase_subscription(
        tenant_id, user_id, INSTALLATION, "test-agent", FCM_TOKEN_TWO, "web", "Chrome"
    )

    tokens = list(
        (
            await db_session.execute(
                select(FirebasePushSubscription).where(
                    FirebasePushSubscription.tenant_id == tenant_id
                )
            )
        ).scalars()
    )
    assert len(tokens) == 2
    by_token = {token.fcm_token: token for token in tokens}
    assert by_token[FCM_TOKEN_ONE].disabled_at is not None
    assert by_token[FCM_TOKEN_TWO].disabled_at is None
    assert by_token[FCM_TOKEN_TWO].provider == "firebase"
    assert by_token[FCM_TOKEN_TWO].platform == "web"


@pytest.mark.asyncio
async def test_delivery_is_deduplicated_per_installation(db_session: AsyncSession) -> None:
    context = await create_tenant_with_user(db_session, "install-dedupe")
    service = UserNotificationService(db_session)
    tenant_id = context["tenant"].id
    user_id = context["user"].id

    # One installation with both providers active: the recipient must receive
    # exactly one push even if both transports are registered.
    await service.save_subscription(
        tenant_id, user_id, INSTALLATION, "web", "test-agent", WEB_ENDPOINT, "p256dh", "auth"
    )
    await service.save_firebase_subscription(
        tenant_id, user_id, INSTALLATION, "test-agent", FCM_TOKEN_ONE, "web", "Chrome"
    )
    await service.enqueue(
        tenant_id=tenant_id,
        event_type="announcement.published",
        recipients=[user_id],
        category="announcements",
        target_path="/announcements",
        deduplication_key="dedupe-installation-1",
    )
    await db_session.commit()

    web_push = FakeWebPushProvider()
    firebase_push = FakeFirebasePushProvider()
    processor = UserNotificationService(
        db_session, web_push_provider=web_push, firebase_push_provider=firebase_push
    )
    completed = await processor.process_outbox()

    assert completed == 1
    assert len(web_push.sent) == 1
    assert len(firebase_push.sent) == 0


@pytest.mark.asyncio
async def test_health_exposes_retry_telemetry(db_session: AsyncSession) -> None:
    context = await create_tenant_with_user(db_session, "install-retry")
    service = UserNotificationService(db_session)
    tenant_id = context["tenant"].id
    user_id = context["user"].id

    await service.save_subscription(
        tenant_id, user_id, INSTALLATION, "web", "test-agent", WEB_ENDPOINT, "p256dh", "auth"
    )
    await service.save_firebase_subscription(
        tenant_id, user_id, INSTALLATION_TWO, "test-agent", FCM_TOKEN_ONE, "web", "Chrome"
    )
    web_subscription = await db_session.scalar(
        select(WebPushSubscription).where(WebPushSubscription.tenant_id == tenant_id)
    )
    fcm_subscription = await db_session.scalar(
        select(FirebasePushSubscription).where(FirebasePushSubscription.tenant_id == tenant_id)
    )
    assert web_subscription is not None and fcm_subscription is not None
    web_subscription.failure_count = 2
    fcm_subscription.failure_count = 1
    await db_session.commit()

    health = await service.health(tenant_id)

    assert health.retrying_web_subscriptions == 1
    assert health.retrying_fcm_tokens == 1


@pytest.mark.asyncio
async def test_registration_endpoint_validates_metadata(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    context = await create_tenant_with_user(db_session, "install-http")
    token = await login(client, context["user"].email, context["password"])
    headers = {"Authorization": f"Bearer {token}"}

    accepted = await client.post(
        "/api/v1/notifications/devices",
        headers=headers,
        json={
            "installation_id": INSTALLATION,
            "platform": "Linux",
            "browser": "Firefox",
            "device_metadata": {"language": "de", "display_mode": "browser"},
        },
    )
    assert accepted.status_code == 204, accepted.text

    oversized = await client.post(
        "/api/v1/notifications/devices",
        headers=headers,
        json={
            "installation_id": INSTALLATION,
            "device_metadata": {f"key-{index}": "value" for index in range(13)},
        },
    )
    assert oversized.status_code == 422

    long_value = await client.post(
        "/api/v1/notifications/devices",
        headers=headers,
        json={
            "installation_id": INSTALLATION,
            "device_metadata": {"language": "x" * 201},
        },
    )
    assert long_value.status_code == 422

    device = await db_session.scalar(
        select(NotificationDevice).where(NotificationDevice.installation_id == INSTALLATION)
    )
    assert device is not None
    assert device.browser == "Firefox"
