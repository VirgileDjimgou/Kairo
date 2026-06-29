from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class IngestionJobHealthItemResponse(BaseModel):
    job_id: UUID
    document_id: UUID
    document_version_id: UUID
    status: str
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class IngestionJobHealthResponse(BaseModel):
    queued_count: int
    processing_count: int
    failed_count: int
    completed_count: int
    retried_count: int
    recent_failures: list[IngestionJobHealthItemResponse]
