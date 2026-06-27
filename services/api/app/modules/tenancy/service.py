from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tenancy.repository import TenancyRepository
from app.modules.tenancy.schemas import TenantResponse


class TenancyService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = TenancyRepository(db)

    async def get_user_tenants(self, user_id: UUID) -> list[TenantResponse]:
        """Return all tenants the current user is an active member of."""
        memberships = await self._repo.get_user_active_memberships(user_id)
        tenants = []
        for membership in memberships:
            tenant = await self._repo.get_tenant_by_id(membership.tenant_id)
            if tenant:
                tenants.append(TenantResponse.model_validate(tenant))
        return tenants

    async def get_tenant(
        self, tenant_id: UUID, requesting_user_id: UUID
    ) -> TenantResponse:
        """
        Return a specific tenant.

        Enforces isolation: the requesting user must be a member.
        """
        membership = await self._repo.get_tenant_user(tenant_id, requesting_user_id)
        if not membership or membership.membership_status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization",
            )
        tenant = await self._repo.get_tenant_by_id(tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        return TenantResponse.model_validate(tenant)
