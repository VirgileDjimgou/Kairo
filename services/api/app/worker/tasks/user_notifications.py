from __future__ import annotations

import asyncio

from app.db.session import async_session_factory
from app.modules.notifications.user_service import UserNotificationService
from app.worker.celery_app import celery_app


@celery_app.task(name="notifications.process_user_outbox")
def process_user_notification_outbox() -> int:
    return asyncio.run(_process())


async def _process() -> int:
    async with async_session_factory() as session:
        return await UserNotificationService(session).process_outbox()
