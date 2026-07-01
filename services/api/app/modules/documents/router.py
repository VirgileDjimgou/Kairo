from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.authorization import require_capability
from app.core.capabilities import CAP_DOCUMENTS_READ, CAP_DOCUMENTS_WRITE
from app.core.dependencies import AuthDep, DbDep, ObjectStorageDep
from app.modules.documents.schemas import (
    BulkUploadResponse,
    DocumentAccessUpdateRequest,
    DocumentListItemResponse,
    IngestionJobResponse,
    IngestionJobRetryResponse,
    UploadDocumentResponse,
)
from app.modules.documents.service import DocumentService
from app.modules.ingestion.service import IngestionService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/", response_model=list[DocumentListItemResponse])
async def list_documents(current: AuthDep, db: DbDep, storage: ObjectStorageDep) -> list[DocumentListItemResponse]:
    require_capability(
        current,
        CAP_DOCUMENTS_READ,
        detail="Document read capability required",
    )
    service = DocumentService(db, storage)
    return await service.list_documents(current.tenant_id)


@router.post("/upload", response_model=UploadDocumentResponse)
async def upload_document(
    current: AuthDep,
    db: DbDep,
    storage: ObjectStorageDep,
    file: UploadFile = File(...),
    title: Annotated[str, Form(min_length=1)] = "",
    description: Annotated[str | None, Form()] = None,
    access_scope: Annotated[str, Form()] = "tenant_public",
    allowed_role_ids: Annotated[list[str] | None, Form()] = None,
) -> UploadDocumentResponse:
    if current.tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")
    require_capability(
        current,
        CAP_DOCUMENTS_WRITE,
        detail="Document governance write capability required",
    )

    service = DocumentService(db, storage)
    return await service.upload_document(
        tenant_id=current.tenant_id,
        user_id=current.user.id,
        file=file,
        title=title,
        description=description,
        access_scope=access_scope,
        allowed_role_ids=allowed_role_ids,
    )


@router.post("/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload_documents(
    current: AuthDep,
    db: DbDep,
    storage: ObjectStorageDep,
    files: Annotated[list[UploadFile], File(...)],
    title_prefix: Annotated[str, Form()] = "",
    description: Annotated[str | None, Form()] = None,
    access_scope: Annotated[str, Form()] = "tenant_public",
    allowed_role_ids: Annotated[list[str] | None, Form()] = None,
) -> BulkUploadResponse:
    if current.tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")
    require_capability(
        current,
        CAP_DOCUMENTS_WRITE,
        detail="Document governance write capability required",
    )
    service = DocumentService(db, storage)
    return await service.upload_documents_bulk(
        tenant_id=current.tenant_id,
        user_id=current.user.id,
        files=files,
        title_prefix=title_prefix,
        description=description,
        access_scope=access_scope,
        allowed_role_ids=allowed_role_ids,
    )


@router.get("/ingestion-jobs/{job_id}", response_model=IngestionJobResponse)
async def get_ingestion_job(
    job_id: UUID,
    current: AuthDep,
    db: DbDep,
    storage: ObjectStorageDep,
) -> IngestionJobResponse:
    if current.tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")
    require_capability(
        current,
        CAP_DOCUMENTS_READ,
        detail="Document read capability required",
    )

    service = IngestionService(db, storage)
    job = await service.get_job_status(current.tenant_id, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingestion job not found")

    return IngestionJobResponse(**job)


@router.patch("/{document_id}/access", response_model=DocumentListItemResponse)
async def update_document_access(
    document_id: UUID,
    current: AuthDep,
    db: DbDep,
    request: DocumentAccessUpdateRequest,
) -> DocumentListItemResponse:
    require_capability(
        current,
        CAP_DOCUMENTS_WRITE,
        detail="Document governance write capability required",
    )
    service = DocumentService(db, storage_provider=None)
    return await service.update_document_access(
        tenant_id=current.tenant_id,
        document_id=document_id,
        request=request,
        actor_user_id=current.user.id,
    )


@router.post("/{document_id}/reindex", response_model=IngestionJobResponse)
async def reindex_document(
    document_id: UUID,
    current: AuthDep,
    db: DbDep,
) -> IngestionJobResponse:
    require_capability(
        current,
        CAP_DOCUMENTS_WRITE,
        detail="Document governance write capability required",
    )
    service = DocumentService(db, storage_provider=None)
    return await service.request_reingestion(
        tenant_id=current.tenant_id,
        document_id=document_id,
        actor_user_id=current.user.id,
    )


@router.post("/ingestion-jobs/{job_id}/retry", response_model=IngestionJobRetryResponse)
async def retry_ingestion_job(
    job_id: UUID,
    current: AuthDep,
    db: DbDep,
    storage: ObjectStorageDep,
) -> IngestionJobRetryResponse:
    require_capability(
        current,
        CAP_DOCUMENTS_WRITE,
        detail="Document governance write capability required",
    )
    service = DocumentService(db, storage)
    return await service.retry_failed_ingestion_job(
        tenant_id=current.tenant_id,
        job_id=job_id,
        actor_user_id=current.user.id,
    )


@router.patch("/{document_id}/archive", response_model=DocumentListItemResponse)
async def archive_document(
    document_id: UUID,
    current: AuthDep,
    db: DbDep,
    storage: ObjectStorageDep,
) -> DocumentListItemResponse:
    require_capability(
        current,
        CAP_DOCUMENTS_WRITE,
        detail="Document governance write capability required",
    )
    service = DocumentService(db, storage)
    return await service.archive_document(
        tenant_id=current.tenant_id,
        document_id=document_id,
        actor_user_id=current.user.id,
    )


@router.patch("/{document_id}/unarchive", response_model=DocumentListItemResponse)
async def unarchive_document(
    document_id: UUID,
    current: AuthDep,
    db: DbDep,
    storage: ObjectStorageDep,
) -> DocumentListItemResponse:
    require_capability(
        current,
        CAP_DOCUMENTS_WRITE,
        detail="Document governance write capability required",
    )
    service = DocumentService(db, storage)
    return await service.unarchive_document(
        tenant_id=current.tenant_id,
        document_id=document_id,
        actor_user_id=current.user.id,
    )
