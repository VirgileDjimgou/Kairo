from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import AuthDep, NotificationsDep
from app.modules.notifications.schemas import (
    NotificationChannelResponse,
    NotificationTestRequest,
    NotificationTestResponse,
)
from app.modules.notifications.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _require_admin(current: AuthDep) -> None:
    if not current.has_role("admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")


@router.get("/channels", response_model=list[NotificationChannelResponse])
async def list_notification_channels(
    current: AuthDep,
    notifications: NotificationsDep,
) -> list[NotificationChannelResponse]:
    _require_admin(current)
    service = NotificationService(notifications)
    return service.list_channels()


@router.post("/test", response_model=NotificationTestResponse)
async def send_test_notification(
    payload: NotificationTestRequest,
    current: AuthDep,
    notifications: NotificationsDep,
) -> NotificationTestResponse:
    _require_admin(current)
    service = NotificationService(notifications)
    return await service.send_test(
        tenant_id=current.tenant_id,
        actor_user_id=current.user.id,
        payload=payload,
    )
