from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.models import Document, DocumentVersion, DocumentChunk, IngestionJob


class DocumentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_document(self, document: Document) -> Document:
        self._db.add(document)
        await self._db.flush()
        await self._db.refresh(document)
        return document

    async def create_version(self, version: DocumentVersion) -> DocumentVersion:
        self._db.add(version)
        await self._db.flush()
        await self._db.refresh(version)
        return version

    async def create_ingestion_job(self, job: IngestionJob) -> IngestionJob:
        self._db.add(job)
        await self._db.flush()
        await self._db.refresh(job)
        return job

    async def list_documents(self, tenant_id: UUID) -> list[tuple[Document, DocumentVersion | None]]:
        result = await self._db.execute(
            select(Document, DocumentVersion)
            .outerjoin(DocumentVersion, Document.current_version_id == DocumentVersion.id)
            .where(Document.tenant_id == tenant_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.all())

    async def get_ingestion_job(self, tenant_id: UUID, job_id: UUID) -> IngestionJob | None:
        result = await self._db.execute(
            select(IngestionJob).where(
                IngestionJob.tenant_id == tenant_id,
                IngestionJob.id == job_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_ingestion_job_by_id(self, job_id: UUID) -> IngestionJob | None:
        result = await self._db.execute(select(IngestionJob).where(IngestionJob.id == job_id))
        return result.scalar_one_or_none()

    async def get_version_for_tenant(
        self, tenant_id: UUID, version_id: UUID
    ) -> DocumentVersion | None:
        result = await self._db.execute(
            select(DocumentVersion).where(
                DocumentVersion.tenant_id == tenant_id,
                DocumentVersion.id == version_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_chunk(self, chunk: DocumentChunk) -> DocumentChunk:
        self._db.add(chunk)
        await self._db.flush()
        return chunk

    async def delete_chunks_for_version(self, tenant_id: UUID, version_id: UUID) -> None:
        await self._db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.tenant_id == tenant_id,
                DocumentChunk.document_version_id == version_id,
            )
        )

    async def count_chunks_for_version(self, tenant_id: UUID, version_id: UUID) -> int:
        result = await self._db.scalar(
            select(func.count())
            .select_from(DocumentChunk)
            .where(
                DocumentChunk.tenant_id == tenant_id,
                DocumentChunk.document_version_id == version_id,
            )
        )
        return int(result or 0)

    async def get_document(self, tenant_id: UUID, document_id: UUID) -> Document | None:
        result = await self._db.execute(
            select(Document).where(
                Document.tenant_id == tenant_id,
                Document.id == document_id,
            )
        )
        return result.scalar_one_or_none()
