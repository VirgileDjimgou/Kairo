from __future__ import annotations

import asyncio
from uuid import UUID

import structlog

from app.core.dependencies import get_object_storage_provider
from app.db.session import async_session_factory
from app.modules.ingestion.service import IngestionService
from app.worker.celery_app import celery_app

logger = structlog.get_logger(__name__)


async def _process_ingestion_job(job_id: UUID) -> None:
    async with async_session_factory() as db:
        service = IngestionService(db, get_object_storage_provider())
        await service.process_job(job_id)


@celery_app.task(name="ingestion.process_job", bind=True, max_retries=2)
def process_ingestion_job(self, job_id: str) -> None:
    try:
        asyncio.run(_process_ingestion_job(UUID(job_id)))
    except Exception as exc:
        logger.exception("ingestion_task_failed", job_id=job_id)
        raise self.retry(exc=exc, countdown=30)


def enqueue_ingestion_job(job_id: UUID) -> None:
    from app.core.config import settings

    if not settings.ingestion_auto_enqueue:
        return

    try:
        process_ingestion_job.delay(str(job_id))
    except Exception as exc:
        logger.warning("ingestion_enqueue_failed", job_id=str(job_id), error=str(exc))
