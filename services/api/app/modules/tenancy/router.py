from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import AuthDep, DbDep
from app.modules.tenancy.schemas import (
    TenantResponse,
    TenantSettingsResponse,
    TenantSettingsUpdate,
)
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


@router.get("/{tenant_id}/settings", response_model=TenantSettingsResponse)
async def get_tenant_settings(
    tenant_id: UUID, current: AuthDep, db: DbDep
) -> TenantSettingsResponse:
    """
    Return tenant settings including branding and module toggles.

    Tenant isolation enforced: user must be an active member.
    """
    service = TenancyService(db)
    return await service.get_tenant_settings(tenant_id, current.user.id)


@router.put("/{tenant_id}/settings", response_model=TenantSettingsResponse)
async def update_tenant_settings(
    tenant_id: UUID,
    settings: TenantSettingsUpdate,
    current: AuthDep,
    db: DbDep,
) -> TenantSettingsResponse:
    """
    Update tenant settings (admin-only).

    Allows updating name, default_language, branding, and module toggles.
    Non-admin members will receive a 403.
    """
    if "admin" not in current.roles:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update tenant settings",
        )
    service = TenancyService(db)
    return await service.update_tenant_settings(tenant_id, current.user.id, settings)
