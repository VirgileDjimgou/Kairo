from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.documents.models import DocumentChunk, DocumentStatus, IngestionJob
from app.modules.documents.repository import DocumentRepository
from app.modules.indexing.service import IndexingService
from app.modules.ingestion.chunking import chunk_text, estimate_token_count
from app.providers.parsers import parse_document_bytes

logger = structlog.get_logger(__name__)


class IngestionService:
    def __init__(
        self,
        db: AsyncSession,
        storage_provider,
        embedding_provider=None,
        vector_store_provider=None,
    ) -> None:
        self._db = db
        self._storage = storage_provider
        self._repo = DocumentRepository(db)
        self._indexing = IndexingService(
            embedding_provider=embedding_provider,
            vector_store_provider=vector_store_provider,
        )

    async def process_job(self, job_id: UUID) -> None:
        job = await self._repo.get_ingestion_job_by_id(job_id)
        if job is None:
            logger.warning("ingestion_job_missing", job_id=str(job_id))
            return

        if job.status in {"completed", "processing"}:
            return

        version = await self._repo.get_version_for_tenant(job.tenant_id, job.document_version_id)
        if version is None:
            await self._mark_failed(job, "Document version not found for tenant")
            return

        document = await self._repo.get_document(job.tenant_id, job.document_id)
        if document is None:
            await self._mark_failed(job, "Document not found for tenant")
            return

        job.status = "processing"
        job.started_at = datetime.now(UTC)
        job.error_message = None
        await self._db.flush()

        try:
            file_bytes = self._storage.download_bytes(version.storage_bucket, version.storage_key)
            text = parse_document_bytes(file_bytes, version.file_name)
            chunk_values = chunk_text(
                text,
                chunk_size=settings.ingestion_chunk_size,
                chunk_overlap=settings.ingestion_chunk_overlap,
            )
            if not chunk_values:
                raise ValueError("No text content extracted from document")

            await self._repo.delete_chunks_for_version(job.tenant_id, job.document_version_id)

            chunks: list[DocumentChunk] = []
            for index, chunk_text_value in enumerate(chunk_values):
                chunk = DocumentChunk(
                    id=uuid4(),
                    tenant_id=job.tenant_id,
                    document_id=job.document_id,
                    document_version_id=job.document_version_id,
                    chunk_index=index,
                    text=chunk_text_value,
                    language=document.language,
                    token_count=estimate_token_count(chunk_text_value),
                )
                await self._repo.create_chunk(chunk)
                chunks.append(chunk)

            indexed_count = await self._indexing.index_chunks(
                document=document,
                document_version_id=job.document_version_id,
                chunks=chunks,
            )

            for chunk in chunks:
                chunk.qdrant_point_id = chunk.id

            document.status = DocumentStatus.ready.value
            job.status = "completed"
            job.finished_at = datetime.now(UTC)
            await self._db.commit()

            logger.info(
                "ingestion_completed",
                job_id=str(job.id),
                tenant_id=str(job.tenant_id),
                chunk_count=len(chunks),
                indexed_count=indexed_count,
            )
        except Exception as exc:
            await self._db.rollback()
            job = await self._repo.get_ingestion_job_by_id(job_id)
            if job is not None:
                await self._mark_failed(job, str(exc))
            logger.exception("ingestion_failed", job_id=str(job_id))

    async def get_job_status(self, tenant_id: UUID, job_id: UUID) -> dict | None:
        job = await self._repo.get_ingestion_job(tenant_id, job_id)
        if job is None:
            return None

        chunk_count = await self._repo.count_chunks_for_version(tenant_id, job.document_version_id)
        indexed_count = await self._repo.count_indexed_chunks_for_version(
            tenant_id, job.document_version_id
        )
        return {
            "id": job.id,
            "document_id": job.document_id,
            "document_version_id": job.document_version_id,
            "status": job.status,
            "error_message": job.error_message,
            "chunk_count": chunk_count,
            "indexed_chunk_count": indexed_count,
            "started_at": job.started_at,
            "finished_at": job.finished_at,
            "created_at": job.created_at,
        }

    async def _mark_failed(self, job: IngestionJob, message: str) -> None:
        job.status = "failed"
        job.error_message = message[:2000]
        job.finished_at = datetime.now(UTC)
        await self._db.commit()
