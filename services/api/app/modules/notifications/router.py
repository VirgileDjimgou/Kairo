from __future__ import annotations

import secrets

from fastapi import APIRouter, Header, HTTPException, Query, status

from app.core.authorization import require_capability
from app.core.capabilities import CAP_TENANT_ADMINISTRATION
from app.core.config import settings
from app.core.dependencies import AuthDep, DbDep, NotificationsDep
from app.core.module_guard import require_module
from app.modules.audit.service import AuditService
from app.modules.notifications.schemas import (
    NotificationChannelResponse,
    NotificationDispatchRequest,
    NotificationDispatchResponse,
    NotificationHistoryResponse,
    NotificationReconciliationCallbackRequest,
    NotificationReconciliationCallbackResponse,
    NotificationReconciliationPollRequest,
    NotificationReconciliationPollResponse,
    NotificationRetryRequest,
    NotificationRetryResponse,
    NotificationTestRequest,
    NotificationTestResponse,
)
from app.modules.notifications.service import NotificationService
from app.modules.notifications.user_schemas import (
    DeviceRegistrationRequest,
    InboxResponse,
    MobilePushTokenRequest,
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate,
    PushConfigurationResponse,
    PushSubscriptionRequest,
    UnreachableNotificationRecipient,
)
from app.modules.notifications.user_service import UserNotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"], dependencies=[require_module("notifications")])
callback_router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/inbox", response_model=InboxResponse)
async def get_user_notification_inbox(current: AuthDep, db: DbDep, limit: int = Query(default=50, ge=1, le=100)) -> InboxResponse:
    return await UserNotificationService(db).inbox(current.tenant_id, current.user.id, limit)


@router.post("/inbox/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_user_notification_read(notification_id: str, current: AuthDep, db: DbDep) -> None:
    from uuid import UUID

    marked = await UserNotificationService(db).mark_read(current.tenant_id, current.user.id, UUID(notification_id))
    if not marked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")


@router.post("/inbox/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_user_notifications_read(current: AuthDep, db: DbDep) -> None:
    await UserNotificationService(db).mark_all_read(current.tenant_id, current.user.id)


@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_user_notification_preferences(current: AuthDep, db: DbDep) -> NotificationPreferencesResponse:
    service = UserNotificationService(db)
    try:
        return await service.preferences(current.tenant_id, current.user.id)
    except RuntimeError:
        return NotificationPreferencesResponse()


@router.put("/preferences", response_model=NotificationPreferencesResponse)
async def update_user_notification_preferences(payload: NotificationPreferencesUpdate, current: AuthDep, db: DbDep) -> NotificationPreferencesResponse:
    service = UserNotificationService(db)
    try:
        return await service.update_preferences(current.tenant_id, current.user.id, payload)
    except RuntimeError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Register this device before updating notification preferences")


@router.get("/push/configuration", response_model=PushConfigurationResponse)
async def get_web_push_configuration(current: AuthDep, db: DbDep) -> PushConfigurationResponse:
    del current
    return PushConfigurationResponse(**await UserNotificationService(db).push_configuration())


@router.post("/devices", status_code=status.HTTP_204_NO_CONTENT)
async def register_notification_device(payload: DeviceRegistrationRequest, current: AuthDep, db: DbDep, user_agent: str | None = Header(default=None)) -> None:
    await UserNotificationService(db).register_device(current.tenant_id, current.user.id, payload.installation_id, payload.platform, user_agent)


@router.post("/push-subscriptions", status_code=status.HTTP_204_NO_CONTENT)
async def subscribe_to_web_push(payload: PushSubscriptionRequest, current: AuthDep, db: DbDep, user_agent: str | None = Header(default=None)) -> None:
    await UserNotificationService(db).save_subscription(current.tenant_id, current.user.id, payload.installation_id, payload.platform, user_agent, payload.endpoint, payload.p256dh, payload.auth)


@router.post("/mobile-push-tokens", status_code=status.HTTP_204_NO_CONTENT)
async def subscribe_to_mobile_push(
    payload: MobilePushTokenRequest,
    current: AuthDep,
    db: DbDep,
    user_agent: str | None = Header(default=None),
) -> None:
    await UserNotificationService(db).save_firebase_subscription(
        current.tenant_id,
        current.user.id,
        payload.installation_id,
        user_agent,
        payload.fcm_token,
    )


@router.get("/unreachable", response_model=list[UnreachableNotificationRecipient])
async def get_unreachable_notification_recipients(current: AuthDep, db: DbDep) -> list[UnreachableNotificationRecipient]:
    require_capability(current, CAP_TENANT_ADMINISTRATION, detail="Tenant administration capability required")
    return await UserNotificationService(db).unreachable_recipients(current.tenant_id)


@router.get("/channels", response_model=list[NotificationChannelResponse])
async def list_notification_channels(
    current: AuthDep,
    notifications: NotificationsDep,
) -> list[NotificationChannelResponse]:
    require_capability(
        current,
        CAP_TENANT_ADMINISTRATION,
        detail="Tenant administration capability required",
    )
    service = NotificationService(notifications)
    return service.list_channels()


@router.post("/test", response_model=NotificationTestResponse)
async def send_test_notification(
    payload: NotificationTestRequest,
    current: AuthDep,
    db: DbDep,
    notifications: NotificationsDep,
) -> NotificationTestResponse:
    require_capability(
        current,
        CAP_TENANT_ADMINISTRATION,
        detail="Tenant administration capability required",
    )
    service = NotificationService(notifications, db=db, audit=AuditService(db))
    return await service.send_test(
        tenant_id=current.tenant_id,
        actor_user_id=current.user.id,
        payload=payload,
    )


@router.post("/dispatch", response_model=NotificationDispatchResponse)
async def send_live_notification(
    payload: NotificationDispatchRequest,
    current: AuthDep,
    db: DbDep,
    notifications: NotificationsDep,
) -> NotificationDispatchResponse:
    require_capability(
        current,
        CAP_TENANT_ADMINISTRATION,
        detail="Tenant administration capability required",
    )
    service = NotificationService(notifications, db=db, audit=AuditService(db))
    return await service.send_live_dispatch(
        tenant_id=current.tenant_id,
        actor_user_id=current.user.id,
        payload=payload,
    )


@router.get("/history", response_model=NotificationHistoryResponse)
async def list_notification_history(
    current: AuthDep,
    db: DbDep,
    notifications: NotificationsDep,
    status_filter: str = Query(
        default="all",
        alias="status",
        pattern="^(all|pending|delivered|failed|simulated)$",
    ),
    stale_only: bool = Query(default=False),
    limit: int = Query(default=20, ge=1, le=100),
) -> NotificationHistoryResponse:
    require_capability(
        current,
        CAP_TENANT_ADMINISTRATION,
        detail="Tenant administration capability required",
    )
    service = NotificationService(notifications, db=db, audit=AuditService(db))
    return await service.list_history(
        tenant_id=current.tenant_id,
        limit=limit,
        status_filter=status_filter,
        stale_only=stale_only,
    )


@callback_router.post(
    "/reconciliation/callback",
    response_model=NotificationReconciliationCallbackResponse,
)
async def receive_notification_reconciliation_callback(
    payload: NotificationReconciliationCallbackRequest,
    db: DbDep,
    notifications: NotificationsDep,
    kairo_notification_token: str | None = Header(default=None, alias="X-Kairo-Notification-Token"),
) -> NotificationReconciliationCallbackResponse:
    configured_token = settings.notification_reconciliation_callback_token
    if not configured_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Notification reconciliation callback is not configured",
        )
    if kairo_notification_token is None or not secrets.compare_digest(
        kairo_notification_token,
        configured_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid notification reconciliation token",
        )

    service = NotificationService(notifications, db=db, audit=AuditService(db))
    return await service.record_provider_reconciliation(payload=payload)


@router.post(
    "/reconciliation/poll",
    response_model=NotificationReconciliationPollResponse,
)
async def poll_notification_reconciliation(
    payload: NotificationReconciliationPollRequest,
    current: AuthDep,
    db: DbDep,
    notifications: NotificationsDep,
) -> NotificationReconciliationPollResponse:
    require_capability(
        current,
        CAP_TENANT_ADMINISTRATION,
        detail="Tenant administration capability required",
    )
    service = NotificationService(notifications, db=db, audit=AuditService(db))
    return await service.poll_provider_reconciliation(
        tenant_id=current.tenant_id,
        actor_user_id=current.user.id,
        payload=payload,
    )


@router.post(
    "/retry",
    response_model=NotificationRetryResponse,
)
async def retry_notification_dispatch(
    payload: NotificationRetryRequest,
    current: AuthDep,
    db: DbDep,
    notifications: NotificationsDep,
) -> NotificationRetryResponse:
    require_capability(
        current,
        CAP_TENANT_ADMINISTRATION,
        detail="Tenant administration capability required",
    )
    service = NotificationService(notifications, db=db, audit=AuditService(db))
    return await service.retry_failed_dispatch(
        tenant_id=current.tenant_id,
        actor_user_id=current.user.id,
        payload=payload,
    )
