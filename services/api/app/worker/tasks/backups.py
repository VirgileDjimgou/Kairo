from __future__ import annotations

import asyncio
from uuid import UUID

from sqlalchemy import select

from app.db.session import async_session_factory
from app.modules.backup.service import BackupService
from app.modules.tenancy.models import Tenant
from app.worker.celery_app import celery_app


@celery_app.task(name="recovery.run_backup")
def run_backup(run_id: str) -> None:
    asyncio.run(_run(UUID(run_id)))


async def _run(run_id: UUID) -> None:
    async with async_session_factory() as session:
        await BackupService(session).execute_run(run_id)


@celery_app.task(name="recovery.run_daily_backup")
def run_daily_backup() -> int:
    return asyncio.run(_daily())


async def _daily() -> int:
    from app.core.config import settings

    if not settings.backup_enabled or not settings.backup_auto_enabled:
        return 0
    async with async_session_factory() as session:
        # A deployment backup is platform-wide and encrypted. The requesting
        # tenant only sees its own recovery ledger row; raw archives are never
        # made visible through the API.
        tenant_id = await session.scalar(select(Tenant.id).order_by(Tenant.created_at).limit(1))
        if tenant_id is None:
            return 0
        service = BackupService(session)
        run = await service.request_backup(tenant_id=tenant_id, actor_user_id=None, trigger="daily")
        await service.execute_run(run.id)
        await service.prune_archives()
        return 1
