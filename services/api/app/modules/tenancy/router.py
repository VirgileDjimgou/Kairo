import json
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, Response, status

from app.core.dependencies import AuthDep, DbDep
from app.modules.tenancy.branding import branding_from_json
from app.modules.tenancy.schemas import (
    PublicTenantResolutionResponse,
    RoleBundleCreate,
    RoleResponse,
    TenantResponse,
    TenantSettingsResponse,
    TenantSettingsUpdate,
)
from app.modules.tenancy.service import TenancyService

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/public/resolve", response_model=PublicTenantResolutionResponse)
async def resolve_public_tenant_host(request: Request, db: DbDep) -> PublicTenantResolutionResponse:
    """Resolve the tenant mapped to the request Host header.

    Server-authoritative: the client never supplies a tenant id or slug. Only an
    exact custom domain or a direct platform subdomain resolves; any other host
    returns 404 so it cannot select a tenant.
    """
    tenant = await TenancyService(db).resolve_host_tenant(request.headers.get("host", ""))
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tenant is mapped to this host",
        )
    return PublicTenantResolutionResponse(
        tenant_id=tenant.id,
        slug=tenant.slug,
        name=tenant.name,
        default_language=tenant.default_language,
        branding=branding_from_json(tenant.branding_json),
        manifest_url=f"/api/v1/tenants/public/{tenant.slug}/manifest",
    )


@router.get("/public/{slug}/manifest")
async def get_public_tenant_manifest(slug: str, request: Request, db: DbDep) -> Response:
    """Public, tenant-aware Web App Manifest built from tenant branding.

    No authentication is required: a manifest is install-time presentation
    data. Only branding values are exposed; settings, roles and members are
    never included, and unknown or inactive tenants are not resolvable.
    """
    manifest = await TenancyService(db).get_public_manifest(slug, str(request.base_url))
    return Response(
        content=json.dumps(manifest),
        media_type="application/manifest+json",
    )


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


@router.get("/{tenant_id}/roles", response_model=list[RoleResponse])
async def list_tenant_roles(
    tenant_id: UUID, current: AuthDep, db: DbDep
) -> list[RoleResponse]:
    """
    Return the roles available in a tenant for admin access operations.

    Tenant isolation enforced and restricted to tenant administrators.
    """
    service = TenancyService(db)
    return await service.get_tenant_roles(tenant_id, current.user.id)


@router.post("/{tenant_id}/roles", response_model=RoleResponse, status_code=201)
async def create_tenant_role_bundle(
    tenant_id: UUID,
    payload: RoleBundleCreate,
    current: AuthDep,
    db: DbDep,
) -> RoleResponse:
    """Create a tenant-specific role bundle over canonical capabilities."""
    service = TenancyService(db)
    return await service.create_role_bundle(tenant_id, current.user.id, payload)


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
    service = TenancyService(db)
    return await service.update_tenant_settings(tenant_id, current.user.id, settings)
