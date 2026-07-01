from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter

from app.core.authorization import require_capability
from app.core.capabilities import (
    CAP_DISCIPLINARY_TENANT_READ,
    CAP_DISCIPLINARY_WRITE,
)
from app.core.dependencies import AuthDep, DbDep
from app.core.module_guard import require_module
from app.modules.disciplinary.schemas import (
    DisciplinaryRecordCreate,
    DisciplinaryRecordResponse,
    DisciplinaryRecordUpdate,
)
from app.modules.disciplinary.service import DisciplinaryService

router = APIRouter(
    prefix="/disciplinary",
    tags=["disciplinary"],
    dependencies=[require_module("disciplinary")],
)


@router.get("/me", response_model=list[DisciplinaryRecordResponse])
async def list_my_records(current: AuthDep, db: DbDep) -> list[DisciplinaryRecordResponse]:
    service = DisciplinaryService(db)
    return await service.list_my_records(current.tenant_id, current.user.id)


@router.get("/", response_model=list[DisciplinaryRecordResponse])
async def list_records(current: AuthDep, db: DbDep) -> list[DisciplinaryRecordResponse]:
    require_capability(
        current,
        CAP_DISCIPLINARY_TENANT_READ,
        detail="Disciplinary read capability required",
    )
    service = DisciplinaryService(db)
    return await service.list_records(current.tenant_id)


@router.get("/{record_id}", response_model=DisciplinaryRecordResponse)
async def get_record(record_id: UUID, current: AuthDep, db: DbDep) -> DisciplinaryRecordResponse:
    service = DisciplinaryService(db)
    return await service.get_record(
        tenant_id=current.tenant_id,
        record_id=record_id,
        user_id=current.user.id,
        can_read_tenant_records=current.has_capability(CAP_DISCIPLINARY_TENANT_READ),
    )


@router.post("/", response_model=DisciplinaryRecordResponse, status_code=201)
async def create_record(
    data: DisciplinaryRecordCreate,
    current: AuthDep,
    db: DbDep,
) -> DisciplinaryRecordResponse:
    require_capability(
        current,
        CAP_DISCIPLINARY_WRITE,
        detail="Disciplinary write capability required",
    )
    service = DisciplinaryService(db)
    return await service.create_record(
        current.tenant_id,
        current.user.id,
        data,
        actor_user_id=current.user.id,
    )


@router.patch("/{record_id}", response_model=DisciplinaryRecordResponse)
async def update_record(
    record_id: UUID,
    data: DisciplinaryRecordUpdate,
    current: AuthDep,
    db: DbDep,
) -> DisciplinaryRecordResponse:
    require_capability(
        current,
        CAP_DISCIPLINARY_WRITE,
        detail="Disciplinary write capability required",
    )
    service = DisciplinaryService(db)
    return await service.update_record(
        current.tenant_id,
        record_id,
        data,
        actor_user_id=current.user.id,
    )


@router.delete("/{record_id}", status_code=204)
async def delete_record(
    record_id: UUID,
    current: AuthDep,
    db: DbDep,
) -> None:
    require_capability(
        current,
        CAP_DISCIPLINARY_WRITE,
        detail="Disciplinary write capability required",
    )
    service = DisciplinaryService(db)
    await service.delete_record(
        current.tenant_id, record_id, actor_user_id=current.user.id
    )
