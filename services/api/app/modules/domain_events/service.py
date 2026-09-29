from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, Self
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.request_context import current_request_id
from app.modules.domain_events.models import (
    EVENT_STATUS_COMPLETED,
    EVENT_STATUS_FAILED,
    EVENT_STATUS_PENDING,
    EVENT_STATUS_PROCESSING,
    DomainEvent,
)
from app.modules.domain_events.registry import (
    DomainEventContext,
    DomainEventHandlerRegistry,
    default_registry,
)
from app.providers.notifications.base import NotificationProvider

MAX_HANDLER_ATTEMPTS = 5
MAX_RETRY_DELAY_MINUTES = 30

logger = structlog.get_logger(__name__)


def _json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


class DomainEventService:
    """Publish internal domain events and apply registered consumer handlers.

    Events are persisted in the caller's transaction, so a committed business
    mutation always has its event. Handlers run inline whenever possible; durable
    pending rows are retried safely by the worker because the outbox records which
    handlers already completed and every projection is idempotent.
    """

    def __init__(
        self, db: AsyncSession, *, registry: DomainEventHandlerRegistry | None = None
    ) -> None:
        self._db = db
        self._registry = registry or default_registry()
        self._context = DomainEventContext()

    def with_notification_providers(self, providers: list[NotificationProvider]) -> Self:
        self._context = DomainEventContext(notification_providers=list(providers))
        return self

    @property
    def context(self) -> DomainEventContext:
        return self._context

    async def publish(
        self,
        *,
        tenant_id: UUID,
        event_type: str,
        aggregate_type: str,
        aggregate_id: UUID | str,
        deduplication_key: str,
        payload: dict[str, Any] | None = None,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
        occurred_at: datetime | None = None,
        dispatch: bool = True,
    ) -> DomainEvent:
        existing = await self._find(tenant_id, deduplication_key)
        if existing is not None:
            return existing

        now = datetime.now(UTC)
        event = DomainEvent(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=str(aggregate_id),
            occurred_at=occurred_at or now,
            correlation_id=correlation_id if correlation_id is not None else current_request_id.get(),
            deduplication_key=deduplication_key,
            payload_json=json.dumps(payload or {}, ensure_ascii=False, default=_json_default),
            applied_handlers_json="[]",
            status=EVENT_STATUS_PENDING,
            available_at=now,
        )
        self._db.add(event)
        await self._db.flush()
        if dispatch:
            await self.dispatch(event)
        return event

    async def dispatch(self, event: DomainEvent) -> bool:
        handlers = self._registry.handlers_for(event.event_type)
        applied = set(event.applied_handlers)
        event.attempts += 1
        event.status = EVENT_STATUS_PROCESSING

        for handler in handlers:
            if handler.name in applied:
                continue
            try:
                await handler.handle(self._db, event, self._context)
            except Exception as exc:
                event.status = (
                    EVENT_STATUS_PENDING
                    if event.attempts < MAX_HANDLER_ATTEMPTS
                    else EVENT_STATUS_FAILED
                )
                event.available_at = datetime.now(UTC) + timedelta(
                    minutes=min(MAX_RETRY_DELAY_MINUTES, 2**event.attempts)
                )
                event.last_error = f"{handler.name}:{type(exc).__name__}"
                logger.warning(
                    "domain_event_handler_failed",
                    event_id=str(event.id),
                    event_type=event.event_type,
                    handler=handler.name,
                    attempts=event.attempts,
                    error=type(exc).__name__,
                )
                await self._db.flush()
                return False
            applied.add(handler.name)
            event.applied_handlers_json = json.dumps(sorted(applied))
            await self._db.flush()

        event.status = EVENT_STATUS_COMPLETED
        event.processed_at = datetime.now(UTC)
        event.last_error = None
        await self._db.flush()
        return True

    async def process_pending(self, batch_size: int = 100) -> int:
        """Worker entry point: retry events that were not fully applied inline."""
        now = datetime.now(UTC)
        result = await self._db.execute(
            select(DomainEvent)
            .where(DomainEvent.status == EVENT_STATUS_PENDING, DomainEvent.available_at <= now)
            .order_by(DomainEvent.created_at)
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )
        completed = 0
        for event in list(result.scalars().all()):
            if await self.dispatch(event):
                completed += 1
            await self._db.commit()
        return completed

    async def _find(self, tenant_id: UUID, deduplication_key: str) -> DomainEvent | None:
        result = await self._db.execute(
            select(DomainEvent).where(
                DomainEvent.tenant_id == tenant_id,
                DomainEvent.deduplication_key == deduplication_key,
            )
        )
        return result.scalar_one_or_none()
