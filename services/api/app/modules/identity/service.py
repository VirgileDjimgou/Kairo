from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.modules.identity.repository import UserRepository
from app.modules.identity.schemas import LoginRequest, TokenResponse
from app.modules.tenancy.repository import TenancyRepository


class AuthService:
    """
    Handles login and token issuance.

    Resolves credentials, tenant membership, and roles before signing
    the JWT. The LLM never participates in this flow.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._user_repo = UserRepository(db)
        self._tenancy_repo = TenancyRepository(db)

    async def login(self, request: LoginRequest) -> TokenResponse:
        # 1. Validate credentials
        user = await self._user_repo.get_by_email(request.email)
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )

        # 2. Resolve active tenant
        if request.tenant_slug:
            tenant = await self._tenancy_repo.get_tenant_by_slug(request.tenant_slug)
            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tenant not found",
                )
            membership = await self._tenancy_repo.get_tenant_user(tenant.id, user.id)
            if not membership or membership.membership_status != "active":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not an active member of this organization",
                )
        else:
            # Default to first active tenant membership
            memberships = await self._tenancy_repo.get_user_active_memberships(user.id)
            if not memberships:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No active organization membership found",
                )
            tenant = await self._tenancy_repo.get_tenant_by_id(memberships[0].tenant_id)

        # 3. Resolve roles for this tenant membership
        roles = await self._tenancy_repo.get_user_role_codes(tenant.id, user.id)

        # 4. Issue token
        token = create_access_token(
            user_id=user.id,
            tenant_id=tenant.id,
            roles=roles,
        )

        # 5. Record login timestamp (fire-and-forget pattern)
        await self._user_repo.update_last_login(user.id)

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            tenant_id=tenant.id,
            user_id=user.id,
        )
