from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.authorization import require_capability
from app.core.capabilities import CAP_BACKUP_CREATE, CAP_BACKUP_READ, CAP_BACKUP_RESTORE_REQUEST
from app.core.dependencies import AuthDep, DbDep
from app.modules.backup.schemas import (
    BackupOverviewResponse,
    BackupRequest,
    BackupRunResponse,
    RestoreImportResponse,
)
from app.modules.backup.service import BackupService

router = APIRouter(prefix="/recovery", tags=["recovery"])


@router.get("/backups", response_model=BackupOverviewResponse)
async def backup_overview(current: AuthDep, db: DbDep) -> BackupOverviewResponse:
    require_capability(current, CAP_BACKUP_READ, detail="Recovery backup read capability required")
    return await BackupService(db).list_overview(current.tenant_id)


@router.post("/backups", response_model=BackupRunResponse, status_code=status.HTTP_202_ACCEPTED)
async def request_backup(payload: BackupRequest, current: AuthDep, db: DbDep) -> BackupRunResponse:
    require_capability(
        current, CAP_BACKUP_CREATE, detail="Recovery backup creation capability required"
    )
    service = BackupService(db)
    try:
        run = await service.request_backup(
            tenant_id=current.tenant_id,
            actor_user_id=current.user.id,
            trigger="manual",
            reason=payload.reason,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    from app.worker.tasks.backups import run_backup

    run_backup.delay(str(run.id))
    return service.to_response(run)


@router.post(
    "/backups/import", response_model=RestoreImportResponse, status_code=status.HTTP_201_CREATED
)
async def import_backup(
    current: AuthDep,
    db: DbDep,
    archive: UploadFile = File(...),
    manifest: UploadFile = File(...),
) -> RestoreImportResponse:
    require_capability(
        current, CAP_BACKUP_RESTORE_REQUEST, detail="Recovery restore request capability required"
    )
    archive_data = await archive.read()
    manifest_data = await manifest.read()
    if len(archive_data) > 2 * 1024 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Backup archive is too large",
        )
    try:
        run = await BackupService(db).stage_import(
            tenant_id=current.tenant_id,
            actor_user_id=current.user.id,
            archive_name=archive.filename or "imported-kairo-backup.enc",
            archive=archive_data,
            manifest=manifest_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return RestoreImportResponse(
        run=BackupService.to_response(run),
        verified=True,
        guidance=(
            "Archive verified and staged. Execute the host-side recovery procedure "
            "with maintenance confirmation."
        ),
    )


@router.get("/backups/{run_id}", response_model=BackupRunResponse)
async def get_backup(run_id: UUID, current: AuthDep, db: DbDep) -> BackupRunResponse:
    require_capability(current, CAP_BACKUP_READ, detail="Recovery backup read capability required")
    run = await BackupService(db).get_owned_run(current.tenant_id, run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup run not found")
    return BackupService.to_response(run)
