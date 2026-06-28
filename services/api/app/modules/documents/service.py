from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
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
from app.modules.documents.schemas import (
    DocumentAccessUpdateRequest,
    DocumentListItemResponse,
    IngestionJobResponse,
    UploadDocumentResponse,
)

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
            allowed_role_ids_json=json.dumps(sorted(set(allowed_role_ids or [])))
            if allowed_role_ids
            else None,
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

    async def update_document_access(
        self,
        *,
        tenant_id: UUID,
        document_id: UUID,
        request: DocumentAccessUpdateRequest,
    ) -> DocumentListItemResponse:
        try:
            document_scope = DocumentAccessScope(request.access_scope).value
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid access scope",
            ) from exc

        allowed_role_ids_json = self._serialize_allowed_role_ids(
            document_scope=document_scope,
            allowed_role_ids=request.allowed_role_ids,
        )
        document = await self._repo.update_document_access(
            tenant_id,
            document_id,
            access_scope=document_scope,
            allowed_role_ids_json=allowed_role_ids_json,
        )
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        document.updated_at = datetime.now(UTC)
        await self._db.commit()

        version = None
        if document.current_version_id is not None:
            version = await self._repo.get_version_for_tenant(tenant_id, document.current_version_id)
        return self._to_list_item(document, version)

    async def request_reingestion(
        self,
        *,
        tenant_id: UUID,
        document_id: UUID,
    ) -> IngestionJobResponse:
        document = await self._repo.get_document(tenant_id, document_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        if document.current_version_id is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document has no active version to ingest",
            )
        version = await self._repo.get_version_for_tenant(tenant_id, document.current_version_id)
        if version is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document version not found",
            )

        job = IngestionJob(
            id=uuid4(),
            tenant_id=tenant_id,
            document_id=document.id,
            document_version_id=version.id,
            status="pending",
            created_at=datetime.now(UTC),
        )
        await self._repo.create_ingestion_job(job)
        await self._db.commit()

        from app.worker.tasks.ingestion import enqueue_ingestion_job

        enqueue_ingestion_job(job.id)

        return IngestionJobResponse(
            id=job.id,
            document_id=job.document_id,
            document_version_id=job.document_version_id,
            status=job.status,
            error_message=job.error_message,
            chunk_count=0,
            indexed_chunk_count=0,
            started_at=job.started_at,
            finished_at=job.finished_at,
            created_at=job.created_at,
        )

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
            allowed_role_ids=self._parse_allowed_role_ids(document.allowed_role_ids_json),
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

    def _parse_allowed_role_ids(self, raw: str | None) -> list[str] | None:
        if not raw:
            return None
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return None
        if not isinstance(parsed, list):
            return None
        return [str(role) for role in parsed]

    def _serialize_allowed_role_ids(
        self,
        *,
        document_scope: str,
        allowed_role_ids: list[str] | None,
    ) -> str | None:
        if document_scope != DocumentAccessScope.role_restricted.value:
            return None
        clean_roles = sorted({role.strip() for role in (allowed_role_ids or []) if role.strip()})
        if not clean_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role restricted documents require at least one allowed role",
            )
        return json.dumps(clean_roles)
