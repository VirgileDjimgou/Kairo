from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.dependencies import AuthDep, DbDep, ObjectStorageDep
from app.modules.documents.schemas import (
    DocumentListItemResponse,
    IngestionJobResponse,
    UploadDocumentResponse,
)
from app.modules.documents.service import DocumentService
from app.modules.ingestion.service import IngestionService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/", response_model=list[DocumentListItemResponse])
async def list_documents(current: AuthDep, db: DbDep, storage: ObjectStorageDep) -> list[DocumentListItemResponse]:
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


@router.get("/ingestion-jobs/{job_id}", response_model=IngestionJobResponse)
async def get_ingestion_job(
    job_id: UUID,
    current: AuthDep,
    db: DbDep,
    storage: ObjectStorageDep,
) -> IngestionJobResponse:
    if current.tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")

    service = IngestionService(db, storage)
    job = await service.get_job_status(current.tenant_id, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingestion job not found")

    return IngestionJobResponse(**job)