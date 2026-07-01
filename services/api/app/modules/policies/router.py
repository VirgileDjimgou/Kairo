from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter

from app.core.authorization import require_capability
from app.core.capabilities import CAP_POLICIES_WRITE
from app.core.dependencies import AuthDep, DbDep
from app.core.module_guard import require_module
from app.modules.policies.schemas import (
    PolicyCategoryResponse,
    PolicyRecordCreate,
    PolicyRecordResponse,
    PolicyRecordUpdate,
)
from app.modules.policies.service import PolicyService

router = APIRouter(
    prefix="/policies",
    tags=["policies"],
    dependencies=[require_module("policies")],
)


@router.get("/public", response_model=list[PolicyRecordResponse])
async def list_public_policies(current: AuthDep, db: DbDep) -> list[PolicyRecordResponse]:
    service = PolicyService(db)
    return await service.list_public(current.tenant_id)


@router.get("/categories", response_model=PolicyCategoryResponse)
async def list_policy_categories(current: AuthDep, db: DbDep) -> PolicyCategoryResponse:
    service = PolicyService(db)
    return await service.list_categories(current.tenant_id)


@router.get("/{policy_id}", response_model=PolicyRecordResponse)
async def get_policy(policy_id: UUID, current: AuthDep, db: DbDep) -> PolicyRecordResponse:
    service = PolicyService(db)
    return await service.get_policy(
        tenant_id=current.tenant_id,
        policy_id=policy_id,
        can_view_unpublished=current.has_capability(CAP_POLICIES_WRITE),
    )


@router.get("/", response_model=list[PolicyRecordResponse])
async def list_policies(current: AuthDep, db: DbDep) -> list[PolicyRecordResponse]:
    require_capability(
        current,
        CAP_POLICIES_WRITE,
        detail="Policy write capability required",
    )
    service = PolicyService(db)
    return await service.list_all(current.tenant_id)


@router.post("/", response_model=PolicyRecordResponse, status_code=201)
async def create_policy(
    data: PolicyRecordCreate,
    current: AuthDep,
    db: DbDep,
) -> PolicyRecordResponse:
    require_capability(
        current,
        CAP_POLICIES_WRITE,
        detail="Policy write capability required",
    )
    service = PolicyService(db)
    return await service.create_policy(
        current.tenant_id, data, current.user.id, actor_user_id=current.user.id
    )


@router.patch("/{policy_id}", response_model=PolicyRecordResponse)
async def update_policy(
    policy_id: UUID,
    data: PolicyRecordUpdate,
    current: AuthDep,
    db: DbDep,
) -> PolicyRecordResponse:
    require_capability(
        current,
        CAP_POLICIES_WRITE,
        detail="Policy write capability required",
    )
    service = PolicyService(db)
    return await service.update_policy(
        current.tenant_id, policy_id, data, actor_user_id=current.user.id
    )


@router.delete("/{policy_id}", status_code=204)
async def delete_policy(
    policy_id: UUID,
    current: AuthDep,
    db: DbDep,
) -> None:
    require_capability(
        current,
        CAP_POLICIES_WRITE,
        detail="Policy write capability required",
    )
    service = PolicyService(db)
    await service.delete_policy(
        current.tenant_id, policy_id, actor_user_id=current.user.id
    )
