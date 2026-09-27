from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID

from sqlalchemy import CursorResult, func, select, update

from app.modules.notifications.user_base import UserNotificationServiceBase
from app.modules.notifications.user_models import (
    NotificationOutboxEvent,
    UserNotification,
)
from app.modules.notifications.user_schemas import (
    InboxNotificationResponse,
    InboxResponse,
)
from app.modules.tenancy.models import Role, TenantUser, UserRole


class InboxMixin(UserNotificationServiceBase):
    async def enqueue(
        self,
        *,
        tenant_id: UUID,
        event_type: str,
        recipients: Iterable[UUID],
        category: str,
        target_path: str,
        deduplication_key: str,
        metadata: dict[str, object] | None = None,
        priority: str = "normal",
        event_id: UUID | None = None,
        correlation_id: str | None = None,
        push_policy: str = "generic",
    ) -> None:
        recipient_ids = sorted({str(user_id) for user_id in recipients})
        if not recipient_ids:
            return
        event = NotificationOutboxEvent(
            tenant_id=tenant_id,
            event_type=event_type,
            deduplication_key=deduplication_key,
            payload_json=json.dumps({
                "recipients": recipient_ids,
                "category": category,
                "target_path": target_path,
                "metadata": metadata or {},
                "priority": priority,
                "event_id": str(event_id) if event_id is not None else None,
                "correlation_id": correlation_id,
                "push_policy": push_policy,
            }, default=str),
        )
        self._db.add(event)
    async def users_with_roles(self, tenant_id: UUID, role_codes: Iterable[str]) -> list[UUID]:
        codes = list(set(role_codes))
        if not codes:
            return []
        result = await self._db.execute(
            select(TenantUser.user_id)
            .select_from(TenantUser)
            .join(UserRole, UserRole.c.tenant_user_id == TenantUser.id)
            .join(Role, Role.id == UserRole.c.role_id)
            .where(TenantUser.tenant_id == tenant_id, TenantUser.membership_status == "active", Role.code.in_(codes))
        )
        return list(set(result.scalars().all()))
    async def active_tenant_users(self, tenant_id: UUID) -> list[UUID]:
        result = await self._db.execute(
            select(TenantUser.user_id).where(
                TenantUser.tenant_id == tenant_id,
                TenantUser.membership_status == "active",
            )
        )
        return list(set(result.scalars().all()))
    async def inbox(self, tenant_id: UUID, user_id: UUID, limit: int = 50) -> InboxResponse:
        result = await self._db.execute(
            select(UserNotification)
            .where(UserNotification.tenant_id == tenant_id, UserNotification.recipient_user_id == user_id)
            .order_by(UserNotification.created_at.desc())
            .limit(limit)
        )
        items = list(result.scalars().all())
        unread = await self._db.scalar(
            select(func.count(UserNotification.id)).where(
                UserNotification.tenant_id == tenant_id,
                UserNotification.recipient_user_id == user_id,
                UserNotification.read_at.is_(None),
            )
        )
        return InboxResponse(
            unread_count=int(unread or 0),
            items=[self._to_response(item) for item in items],
        )
    async def mark_read(self, tenant_id: UUID, user_id: UUID, notification_id: UUID) -> bool:
        result = await self._db.execute(
            update(UserNotification)
            .where(UserNotification.id == notification_id, UserNotification.tenant_id == tenant_id, UserNotification.recipient_user_id == user_id)
            .values(read_at=datetime.now(UTC))
        )
        await self._db.commit()
        return bool(cast(CursorResult[Any], result).rowcount)
    async def mark_all_read(self, tenant_id: UUID, user_id: UUID) -> None:
        await self._db.execute(
            update(UserNotification)
            .where(UserNotification.tenant_id == tenant_id, UserNotification.recipient_user_id == user_id, UserNotification.read_at.is_(None))
            .values(read_at=datetime.now(UTC))
        )
        await self._db.commit()
    def _to_response(self, item: UserNotification) -> InboxNotificationResponse:
        try:
            metadata = json.loads(item.metadata_json)
        except json.JSONDecodeError:
            metadata = {}
        return InboxNotificationResponse(id=item.id, event_type=item.event_type, category=item.category, priority=item.priority, target_path=item.target_path, event_id=item.event_id, correlation_id=item.correlation_id, metadata=metadata if isinstance(metadata, dict) else {}, read_at=item.read_at, created_at=item.created_at)
