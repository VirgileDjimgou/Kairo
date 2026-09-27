from __future__ import annotations

import asyncio

from app.core.dependencies import get_notification_providers
from app.db.session import async_session_factory
from app.modules.domain_events.service import DomainEventService
from app.worker.celery_app import celery_app


@celery_app.task(name="domain_events.process_outbox")
def process_domain_event_outbox() -> int:
    return asyncio.run(_process())


async def _process() -> int:
    async with async_session_factory() as session:
        service = DomainEventService(session).with_notification_providers(
            get_notification_providers()
        )
        return await service.process_pending()
