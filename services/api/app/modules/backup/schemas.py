from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BackupRunResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    trigger: str
    status: str
    storage_reference: str | None
    archive_sha256: str | None
    manifest_sha256: str | None
    archive_size_bytes: int | None
    components: dict[str, object]
    error_code: str | None
    requested_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    verified_at: datetime | None


class BackupRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=300)


class BackupOverviewResponse(BaseModel):
    automatic_enabled: bool
    retention_days: int
    external_storage_configured: bool
    point_in_time_recovery_enabled: bool
    last_successful_backup_at: datetime | None
    last_restore_drill_at: datetime | None
    runs: list[BackupRunResponse]


class RestoreImportResponse(BaseModel):
    run: BackupRunResponse
    verified: bool
    guidance: str
