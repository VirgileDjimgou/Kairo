from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import AuthDep, DbDep
from app.modules.disciplinary.schemas import (
    DisciplinaryRecordCreate,
    DisciplinaryRecordResponse,
    DisciplinaryRecordUpdate,
)
from app.modules.disciplinary.service import DisciplinaryService

router = APIRouter(prefix="/disciplinary", tags=["disciplinary"])


def _is_staff(current: AuthDep) -> bool:
    return current.has_role("admin", "treasurer")


@router.get("/me", response_model=list[DisciplinaryRecordResponse])
async def list_my_records(current: AuthDep, db: DbDep) -> list[DisciplinaryRecordResponse]:
    service = DisciplinaryService(db)
    return await service.list_my_records(current.tenant_id, current.user.id)


@router.get("/", response_model=list[DisciplinaryRecordResponse])
async def list_records(current: AuthDep, db: DbDep) -> list[DisciplinaryRecordResponse]:
    if not _is_staff(current):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or treasurer role required")
    service = DisciplinaryService(db)
    return await service.list_records(current.tenant_id)


@router.get("/{record_id}", response_model=DisciplinaryRecordResponse)
async def get_record(record_id: UUID, current: AuthDep, db: DbDep) -> DisciplinaryRecordResponse:
    service = DisciplinaryService(db)
    return await service.get_record(
        tenant_id=current.tenant_id,
        record_id=record_id,
        user_id=current.user.id,
        is_admin_or_treasurer=_is_staff(current),
    )


@router.post("/", response_model=DisciplinaryRecordResponse, status_code=201)
async def create_record(
    data: DisciplinaryRecordCreate,
    current: AuthDep,
    db: DbDep,
) -> DisciplinaryRecordResponse:
    if not _is_staff(current):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or treasurer role required")
    service = DisciplinaryService(db)
    return await service.create_record(current.tenant_id, current.user.id, data)


@router.patch("/{record_id}", response_model=DisciplinaryRecordResponse)
async def update_record(
    record_id: UUID,
    data: DisciplinaryRecordUpdate,
    current: AuthDep,
    db: DbDep,
) -> DisciplinaryRecordResponse:
    if not _is_staff(current):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or treasurer role required")
    service = DisciplinaryService(db)
    return await service.update_record(current.tenant_id, record_id, data)


@router.delete("/{record_id}", status_code=204)
async def delete_record(
    record_id: UUID,
    current: AuthDep,
    db: DbDep,
) -> None:
    if not current.has_role("admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    service = DisciplinaryService(db)
    await service.delete_record(current.tenant_id, record_id)
