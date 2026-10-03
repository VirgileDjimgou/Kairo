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


@celery_app.task(name="notifications.reconcile_user_outbox")
def reconcile_user_notification_outbox() -> dict[str, int]:
    """Reclaim expired processing leases and report outbox health.

    The regular process task already reclaims before claiming; this task makes
    stranded/retrying/dead-letter counts explicit for operators and health
    dashboards even when no new events are pending.
    """
    return asyncio.run(_reconcile())


async def _reconcile() -> dict[str, int]:
    async with async_session_factory() as session:
        return await UserNotificationService(session).reconcile_outbox()
