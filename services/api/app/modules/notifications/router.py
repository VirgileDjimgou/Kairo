from __future__ import annotations

import secrets

from fastapi import APIRouter, Header, HTTPException, status

from app.core.capabilities import CAP_TENANT_ADMINISTRATION
from app.core.config import settings
from app.core.authorization import require_capability
from app.core.dependencies import AuthDep, DbDep, NotificationsDep
from app.modules.audit.service import AuditService
from app.core.module_guard import require_module
from app.modules.notifications.schemas import (
    NotificationChannelResponse,
    NotificationDispatchRequest,
    NotificationDispatchResponse,
    NotificationHistoryEntry,
    NotificationReconciliationCallbackRequest,
    NotificationReconciliationCallbackResponse,
    NotificationTestRequest,
    NotificationTestResponse,
)
from app.modules.notifications.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"], dependencies=[require_module("notifications")])
callback_router = APIRouter(prefix="/notifications", tags=["notifications"])


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


@router.get("/history", response_model=list[NotificationHistoryEntry])
async def list_notification_history(
    current: AuthDep,
    db: DbDep,
    notifications: NotificationsDep,
) -> list[NotificationHistoryEntry]:
    require_capability(
        current,
        CAP_TENANT_ADMINISTRATION,
        detail="Tenant administration capability required",
    )
    service = NotificationService(notifications, db=db, audit=AuditService(db))
    return await service.list_history(tenant_id=current.tenant_id)


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
