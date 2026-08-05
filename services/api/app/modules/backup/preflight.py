from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.backup.service import BackupService


async def require_pre_operation_backup(
    db: AsyncSession, *, tenant_id: UUID, actor_user_id: UUID, reason: str
) -> None:
    """Create and verify a snapshot before an irreversible bulk action.

    The operation is deliberately blocked when recovery protection is not
    available; a destructive action must never silently continue without its
    promised recovery point.
    """
    service = BackupService(db)
    try:
        run = await service.request_backup(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            trigger="pre_operation",
            reason=reason,
        )
        completed = await service.execute_run(run.id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Safety backup could not be completed; the operation was not performed",
        ) from exc
    if completed.status != "available":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Safety backup could not be verified; the operation was not performed",
        )
