from __future__ import annotations

import asyncio
from uuid import UUID

import structlog

from app.core.config import settings
from app.core.dependencies import (
    get_embedding_provider,
    get_object_storage_provider,
    get_vector_store_provider,
)
from app.db.session import async_session_factory
from app.modules.documents.repository import DocumentRepository
from app.modules.ingestion.service import IngestionService
from app.worker.celery_app import celery_app

logger = structlog.get_logger(__name__)


async def _process_ingestion_job(job_id: UUID) -> None:
    async with async_session_factory() as db:
        embedding_provider = None
        vector_store_provider = None
        if settings.ai_runtime_enabled:
            embedding_provider = get_embedding_provider()
            vector_store_provider = get_vector_store_provider()
        service = IngestionService(
            db,
            get_object_storage_provider(),
            embedding_provider=embedding_provider,
            vector_store_provider=vector_store_provider,
        )
        await service.process_job(job_id)


@celery_app.task(name="ingestion.process_job", bind=True, max_retries=2)
def process_ingestion_job(self, job_id: str) -> None:
    try:
        asyncio.run(_process_ingestion_job(UUID(job_id)))
    except Exception as exc:
        logger.exception("ingestion_task_failed", job_id=job_id)
        raise self.retry(exc=exc, countdown=30) from exc


def enqueue_ingestion_job(job_id: UUID) -> None:
    if not settings.ingestion_auto_enqueue:
        return

    try:
        process_ingestion_job.delay(str(job_id))
    except Exception as exc:
        logger.warning("ingestion_enqueue_failed", job_id=str(job_id), error=str(exc))


@celery_app.task(name="ingestion.resume_awaiting_ai_jobs")
def resume_awaiting_ai_jobs() -> int:
    if not settings.ai_runtime_enabled:
        return 0

    async def _resume() -> list[UUID]:
        async with async_session_factory() as db:
            return [job.id for job in await DocumentRepository(db).list_awaiting_ai_jobs()]

    job_ids = asyncio.run(_resume())
    for job_id in job_ids:
        process_ingestion_job.delay(str(job_id))
    return len(job_ids)
