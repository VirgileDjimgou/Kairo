from datetime import UTC, datetime
from uuid import UUID

import jwt
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_mfa_token,
    decode_access_token,
    verify_password,
    verify_totp,
)
from app.modules.identity.base import IdentityServiceBase, _ensure_aware
from app.modules.identity.schemas import (
    LoginRequest,
    MfaCompleteLoginRequest,
    MfaLoginResponse,
    MfaRequiredResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TokenResponse,
)


class AuthenticationMixin(IdentityServiceBase):
    async def login(self, request: LoginRequest) -> TokenResponse | MfaRequiredResponse:
        user = await self._user_repo.get_by_login(request.email)
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid identifier or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )

        if (
            user.password_change_required
            and user.temporary_password_expires_at is not None
            and datetime.now(UTC) > _ensure_aware(user.temporary_password_expires_at)
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Temporary access has expired. Ask an authorized office role to issue a new password.",
            )

        tenant = await self._resolve_login_tenant(request, user.id)

        # If MFA is enabled, issue a short-lived MFA token instead of full JWT
        if user.totp_enabled:
            mfa_token = create_mfa_token(user.id, tenant.id)
            return MfaRequiredResponse(
                mfa_required=True,
                mfa_token=mfa_token,
                expires_in=300,
            )

        roles = await self._tenancy_repo.get_user_role_codes(tenant.id, user.id)
        token, _session_id = await self._issue_session_access_token(
            user_id=user.id,
            tenant_id=tenant.id,
            roles=roles,
        )
        await self._user_repo.update_last_login(user.id)
        await self._audit.record_event(
            tenant_id=tenant.id,
            actor_user_id=user.id,
            action="login_succeeded",
            entity_type="session",
            entity_id=_session_id,
            module_key="identity",
            details={
                "tenant_id": tenant.id,
                "mfa_completed": False,
            },
        )
        await self._db.commit()

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            tenant_id=tenant.id,
            user_id=user.id,
            password_change_required=user.password_change_required,
        )
    async def complete_mfa_login(
        self, request: MfaCompleteLoginRequest
    ) -> MfaLoginResponse:
        try:
            payload = decode_access_token(request.mfa_token)
            if payload.get("type") != "mfa":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA token",
                )
            user_id = UUID(payload["sub"])
            tenant_id = UUID(payload["tenant_id"]) if payload.get("tenant_id") else None
        except (jwt.PyJWTError, ValueError, KeyError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired MFA token",
            ) from None

        user = await self._user_repo.get_by_id(user_id)
        if not user or user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        if (
            user.password_change_required
            and user.temporary_password_expires_at is not None
            and datetime.now(UTC) > _ensure_aware(user.temporary_password_expires_at)
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Temporary access has expired. Ask an authorized office role to issue a new password.",
            )
        if not user.totp_secret or not user.totp_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is not enabled for this account",
            )
        if not verify_totp(user.totp_secret, request.code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid TOTP code",
            )

        if tenant_id is not None:
            tenant = await self._tenancy_repo.get_tenant_by_id(tenant_id)
            membership = (
                await self._tenancy_repo.get_tenant_user(tenant_id, user.id)
                if tenant is not None
                else None
            )
            if (
                tenant is None
                or membership is None
                or membership.membership_status != "active"
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No active organization membership found",
                )
        else:
            memberships = await self._tenancy_repo.get_user_active_memberships(user.id)
            if not memberships:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No active organization membership found",
                )
            tenant = await self._tenancy_repo.get_tenant_by_id(memberships[0].tenant_id)
            if tenant is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization not found",
                )

        roles = await self._tenancy_repo.get_user_role_codes(tenant.id, user.id)
        token, session_id = await self._issue_session_access_token(
            user_id=user.id,
            tenant_id=tenant.id,
            roles=roles,
        )
        await self._user_repo.update_last_login(user.id)
        await self._audit.record_event(
            tenant_id=tenant.id,
            actor_user_id=user.id,
            action="login_succeeded",
            entity_type="session",
            entity_id=session_id,
            module_key="identity",
            details={
                "tenant_id": tenant.id,
                "mfa_completed": True,
            },
        )
        await self._db.commit()

        return MfaLoginResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            tenant_id=tenant.id,
            user_id=user.id,
            password_change_required=user.password_change_required,
        )
    async def refresh_token(
        self, request: RefreshTokenRequest
    ) -> RefreshTokenResponse:
        try:
            payload = decode_access_token(request.refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )
            user_id = UUID(payload["sub"])
            session_id = UUID(payload["sid"])
        except (jwt.PyJWTError, ValueError, KeyError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            ) from None

        user = await self._user_repo.get_by_id(user_id)
        if not user or user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Issue a new refresh token alongside the access token
        memberships = await self._tenancy_repo.get_user_active_memberships(user_id)
        if not memberships:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No active organization membership",
            )

        session = await self._session_repo.get_active_by_id(session_id)
        if session is None or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        session_membership = await self._tenancy_repo.get_tenant_user(
            session.current_tenant_id, user_id
        )
        if (
            session_membership is None
            or session_membership.membership_status != "active"
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The active session organization access is no longer valid",
            )

        tenant = await self._tenancy_repo.get_tenant_by_id(session.current_tenant_id)
        if tenant is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The active session organization no longer exists",
            )
        roles = await self._tenancy_repo.get_user_role_codes(tenant.id, user_id)
        new_access = create_access_token(
            user_id=user_id,
            tenant_id=tenant.id,
            roles=roles,
            session_id=session_id,
        )
        await self._session_repo.touch(
            session_id,
            tenant_id=tenant.id,
            ip_address=self._request_ip,
            user_agent=self._request_user_agent,
        )
        await self._db.commit()

        return RefreshTokenResponse(
            access_token=new_access,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )
    async def _resolve_login_tenant(
        self, request: LoginRequest, user_id: UUID
    ):
        if request.tenant_slug:
            tenant = await self._tenancy_repo.get_tenant_by_slug(request.tenant_slug)
            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tenant not found",
                )
            membership = await self._tenancy_repo.get_tenant_user(tenant.id, user_id)
            if not membership or membership.membership_status != "active":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not an active member of this organization",
                )
        else:
            memberships = await self._tenancy_repo.get_user_active_memberships(user_id)
            if not memberships:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No active organization membership found",
                )
            tenant = await self._tenancy_repo.get_tenant_by_id(memberships[0].tenant_id)
        return tenant
