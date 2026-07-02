from __future__ import annotations

from fastapi import APIRouter

from app.core.capabilities import CAP_TENANT_ADMINISTRATION
from app.core.authorization import require_capability
from app.core.dependencies import AuthDep, DbDep, NotificationsDep
from app.modules.audit.service import AuditService
from app.core.module_guard import require_module
from app.modules.notifications.schemas import (
    NotificationChannelResponse,
    NotificationTestRequest,
    NotificationTestResponse,
)
from app.modules.notifications.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"], dependencies=[require_module("notifications")])


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
