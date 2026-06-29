from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentVersionResponse(BaseModel):
    id: UUID
    file_name: str
    mime_type: str
    file_size_bytes: int
    storage_bucket: str
    storage_key: str
    checksum: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListItemResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    source_type: str
    language: str
    access_scope: str
    allowed_role_ids: list[str] | None = None
    status: str
    owner_user_id: UUID | None
    created_at: datetime
    current_version: DocumentVersionResponse | None = None


class UploadDocumentResponse(DocumentListItemResponse):
    ingestion_job_id: UUID
    current_version: DocumentVersionResponse | None = None
    duplicate_of_document_id: UUID | None = None


class BulkUploadItemResponse(BaseModel):
    index: int
    file_name: str
    status: str
    document: UploadDocumentResponse | None = None
    error: str | None = None


class BulkUploadResponse(BaseModel):
    items: list[BulkUploadItemResponse] = Field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0


class UploadResultResponse(BaseModel):
    documents: list[DocumentListItemResponse] = Field(default_factory=list)


class DocumentAccessUpdateRequest(BaseModel):
    access_scope: str = Field(min_length=1, max_length=50)
    allowed_role_ids: list[str] | None = None


class IngestionJobResponse(BaseModel):
    id: UUID
    document_id: UUID
    document_version_id: UUID
    status: str
    error_message: str | None
    chunk_count: int
    indexed_chunk_count: int
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class IngestionJobRetryResponse(BaseModel):
    job: IngestionJobResponse
    retried: bool = True
