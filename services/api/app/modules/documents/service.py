from __future__ import annotations

import hashlib
import os
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.documents.models import (
    Document,
    DocumentAccessScope,
    DocumentStatus,
    DocumentVersion,
    IngestionJob,
)
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import DocumentListItemResponse, UploadDocumentResponse

ALLOWED_MIME_TYPES: dict[str, set[str]] = {
    "pdf": {"application/pdf"},
    "docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    "txt": {"text/plain"},
    "md": {"text/plain", "text/markdown"},
    "csv": {"text/csv", "application/csv", "text/plain"},
    "png": {"image/png"},
    "jpg": {"image/jpeg"},
    "jpeg": {"image/jpeg"},
    "webp": {"image/webp"},
}


class DocumentService:
    def __init__(self, db: AsyncSession, storage_provider) -> None:
        self._db = db
        self._storage = storage_provider
        self._repo = DocumentRepository(db)

    async def upload_document(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
        file: UploadFile,
        title: str,
        description: str | None,
        access_scope: str,
        allowed_role_ids: list[str] | None = None,
    ) -> UploadDocumentResponse:
        ext = self._get_extension(file.filename)
        self._validate_upload(file, ext)

        document_id = uuid4()
        version_id = uuid4()
        ingestion_job_id = uuid4()
        file_bytes = await file.read()
        if len(file_bytes) > settings.max_upload_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File exceeds the maximum upload size",
            )
        checksum = hashlib.sha256(file_bytes).hexdigest()
        storage_key = self._build_storage_key(tenant_id, document_id, version_id, file.filename)

        self._storage.upload_bytes(
            bucket=settings.minio_bucket_documents,
            object_key=storage_key,
            data=file_bytes,
            content_type=file.content_type or "application/octet-stream",
        )

        try:
            document_scope = DocumentAccessScope(access_scope).value
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access scope") from exc

        document = Document(
            id=document_id,
            tenant_id=tenant_id,
            title=title.strip(),
            description=description.strip() if description else None,
            source_type="upload",
            language="en",
            access_scope=document_scope,
            owner_user_id=user_id,
            status=DocumentStatus.uploaded.value,
            current_version_id=version_id,
            created_by=user_id,
        )
        version = DocumentVersion(
            id=version_id,
            tenant_id=tenant_id,
            document_id=document_id,
            version_number=1,
            file_name=file.filename or "upload",
            mime_type=file.content_type or "application/octet-stream",
            file_size_bytes=len(file_bytes),
            storage_bucket=settings.minio_bucket_documents,
            storage_key=storage_key,
            checksum=checksum,
            created_by=user_id,
        )
        job = IngestionJob(
            id=ingestion_job_id,
            tenant_id=tenant_id,
            document_id=document_id,
            document_version_id=version_id,
            status="pending",
        )

        await self._repo.create_document(document)
        await self._repo.create_version(version)
        await self._repo.create_ingestion_job(job)
        await self._db.commit()

        from app.worker.tasks.ingestion import enqueue_ingestion_job

        enqueue_ingestion_job(job.id)

        return UploadDocumentResponse(
            id=document.id,
            title=document.title,
            description=document.description,
            source_type=document.source_type,
            language=document.language,
            access_scope=document.access_scope,
            status=document.status,
            owner_user_id=document.owner_user_id,
            created_at=document.created_at,
            current_version={
                "id": version.id,
                "file_name": version.file_name,
                "mime_type": version.mime_type,
                "file_size_bytes": version.file_size_bytes,
                "storage_bucket": version.storage_bucket,
                "storage_key": version.storage_key,
                "checksum": version.checksum,
                "created_at": version.created_at,
            },
            ingestion_job_id=job.id,
        )

    async def list_documents(self, tenant_id: UUID) -> list[DocumentListItemResponse]:
        rows = await self._repo.list_documents(tenant_id)
        return [self._to_list_item(document, version) for document, version in rows]

    def _to_list_item(
        self, document: Document, version: DocumentVersion | None
    ) -> DocumentListItemResponse:
        current_version = None
        if version is not None:
            current_version = {
                "id": version.id,
                "file_name": version.file_name,
                "mime_type": version.mime_type,
                "file_size_bytes": version.file_size_bytes,
                "storage_bucket": version.storage_bucket,
                "storage_key": version.storage_key,
                "checksum": version.checksum,
                "created_at": version.created_at,
            }

        return DocumentListItemResponse(
            id=document.id,
            title=document.title,
            description=document.description,
            source_type=document.source_type,
            language=document.language,
            access_scope=document.access_scope,
            status=document.status,
            owner_user_id=document.owner_user_id,
            created_at=document.created_at,
            current_version=current_version,
        )

    def _validate_upload(self, file: UploadFile, extension: str) -> None:
        if extension not in settings.allowed_extensions_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file extension",
            )

        allowed_mimes = ALLOWED_MIME_TYPES.get(extension, set())
        content_type = file.content_type or ""
        if content_type not in allowed_mimes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported MIME type",
            )

    def _get_extension(self, filename: str | None) -> str:
        return Path(filename or "").suffix.lower().lstrip(".")

    def _build_storage_key(self, tenant_id: UUID, document_id: UUID, version_id: UUID, filename: str | None) -> str:
        safe_name = Path(filename or "upload").name.replace(" ", "_")
        return f"tenants/{tenant_id}/documents/{document_id}/versions/{version_id}/{safe_name}"