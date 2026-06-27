from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import AuthDep, DbDep
from app.modules.tenancy.schemas import TenantResponse
from app.modules.tenancy.service import TenancyService

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/", response_model=list[TenantResponse])
async def list_my_tenants(current: AuthDep, db: DbDep) -> list[TenantResponse]:
    """Return all organizations the current user is a member of."""
    service = TenancyService(db)
    return await service.get_user_tenants(current.user.id)


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID, current: AuthDep, db: DbDep
) -> TenantResponse:
    """
    Return a specific organization.

    Returns 403 if the current user is not a member — enforcing tenant isolation.
    """
    service = TenancyService(db)
    return await service.get_tenant(tenant_id, current.user.id)
