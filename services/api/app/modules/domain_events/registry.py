from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.domain_events.models import DomainEvent
from app.providers.notifications.base import NotificationProvider


@dataclass(slots=True)
class DomainEventContext:
    """Runtime collaborators a consumer handler may need.

    Delivery transports stay on the consumer side; producers only emit facts.
    """

    notification_providers: list[NotificationProvider] = field(default_factory=list)


class DomainEventHandler(Protocol):
    name: str

    def supports(self, event_type: str) -> bool: ...

    async def handle(
        self, db: AsyncSession, event: DomainEvent, context: DomainEventContext
    ) -> None: ...


class DomainEventHandlerRegistry:
    def __init__(self) -> None:
        self._handlers: list[DomainEventHandler] = []

    def register(self, handler: DomainEventHandler) -> None:
        self._handlers.append(handler)

    def handlers_for(self, event_type: str) -> list[DomainEventHandler]:
        return [handler for handler in self._handlers if handler.supports(event_type)]

    def handler_names(self) -> list[str]:
        return [handler.name for handler in self._handlers]


_default_registry: DomainEventHandlerRegistry | None = None


def default_registry() -> DomainEventHandlerRegistry:
    """Compose consumer handlers.

    Consumer modules own their projections; business modules emit events and never
    import or construct the consuming transport implementations.
    """
    global _default_registry
    if _default_registry is None:
        registry = DomainEventHandlerRegistry()

        from app.modules.audit.event_handlers import register_audit_handlers
        from app.modules.notifications.event_handlers import register_notification_handlers

        register_audit_handlers(registry)
        register_notification_handlers(registry)
        _default_registry = registry
    return _default_registry
