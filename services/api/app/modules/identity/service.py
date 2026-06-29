import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.audit.service import AuditService


def _ensure_aware(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware (assume UTC if naive)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
from app.core.security import (
    create_access_token,
    create_mfa_token,
    create_refresh_token,
    decode_access_token,
    generate_totp_secret,
    generate_token,
    get_totp_uri,
    hash_password,
    hash_token,
    verify_password,
    verify_totp,
    verify_token,
)
from app.modules.identity.repository import (
    InvitationRepository,
    PasswordResetRepository,
    UserRepository,
)
from app.modules.identity.schemas import (
    AcceptInviteRequest,
    AcceptInviteResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    InvitationStatusResponse,
    InviteRequest,
    InviteResponse,
    LoginRequest,
    MfaCompleteLoginRequest,
    MfaEnrollResponse,
    MfaLoginResponse,
    MfaRequiredResponse,
    MfaVerifyRequest,
    MfaVerifyResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SwitchTenantRequest,
    SwitchTenantResponse,
    TenantMembershipResponse,
    TokenResponse,
)
from app.modules.tenancy.module_toggles import parse_module_toggles
from app.modules.tenancy.repository import TenancyRepository
from app.modules.tenancy.schemas import BrandingConfig, ModuleToggles


class AuthService:
    """
    Handles login, membership resolution, token issuance, and
    identity lifecycle flows (invitation, password reset, MFA).
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._user_repo = UserRepository(db)
        self._tenancy_repo = TenancyRepository(db)
        self._invitation_repo = InvitationRepository(db)
        self._password_reset_repo = PasswordResetRepository(db)
        self._audit = AuditService(db)

    # ── Login / Session ───────────────────────────────────────────────────────

    async def login(self, request: LoginRequest) -> TokenResponse | MfaRequiredResponse:
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

        # If MFA is enabled, issue a short-lived MFA token instead of full JWT
        if user.totp_enabled:
            mfa_token = create_mfa_token(user.id)
            return MfaRequiredResponse(
                mfa_required=True,
                mfa_token=mfa_token,
                expires_in=300,
            )

        # Resolve tenant
        tenant = await self._resolve_login_tenant(request, user.id)
        roles = await self._tenancy_repo.get_user_role_codes(tenant.id, user.id)
        token = create_access_token(
            user_id=user.id,
            tenant_id=tenant.id,
            roles=roles,
        )
        await self._user_repo.update_last_login(user.id)
        await self._db.commit()

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            tenant_id=tenant.id,
            user_id=user.id,
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
        except (jwt.PyJWTError, ValueError, KeyError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired MFA token",
            )

        user = await self._user_repo.get_by_id(user_id)
        if not user or user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
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

        # Resolve the tenant from active memberships
        memberships = await self._tenancy_repo.get_user_active_memberships(user.id)
        if not memberships:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No active organization membership found",
            )
        tenant = await self._tenancy_repo.get_tenant_by_id(memberships[0].tenant_id)
        roles = await self._tenancy_repo.get_user_role_codes(tenant.id, user.id)
        token = create_access_token(
            user_id=user.id,
            tenant_id=tenant.id,
            roles=roles,
        )
        await self._user_repo.update_last_login(user.id)
        await self._db.commit()

        return MfaLoginResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            tenant_id=tenant.id,
            user_id=user.id,
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

    async def get_user_memberships(
        self, user_id: UUID
    ) -> list[TenantMembershipResponse]:
        memberships = await self._tenancy_repo.get_user_active_memberships(user_id)
        result: list[TenantMembershipResponse] = []
        for tu in memberships:
            tenant = await self._tenancy_repo.get_tenant_by_id(tu.tenant_id)
            if not tenant:
                continue
            roles = await self._tenancy_repo.get_user_role_codes(tenant.id, user_id)

            branding_raw = {}
            if isinstance(tenant.branding_json, str) and tenant.branding_json.strip():
                try:
                    branding_raw = json.loads(tenant.branding_json)
                except json.JSONDecodeError:
                    branding_raw = {}

            settings_raw = {}
            if isinstance(tenant.settings_json, str) and tenant.settings_json.strip():
                try:
                    settings_raw = json.loads(tenant.settings_json)
                except json.JSONDecodeError:
                    settings_raw = {}

            module_toggles = parse_module_toggles(settings_raw)
            branding = BrandingConfig(**branding_raw) if branding_raw else BrandingConfig()

            result.append(
                TenantMembershipResponse(
                    tenant_id=tenant.id,
                    slug=tenant.slug,
                    name=tenant.name,
                    roles=roles,
                    branding=branding,
                    modules=ModuleToggles(**module_toggles),
                    profile_type=tu.profile_type,
                )
            )
        return result

    async def switch_tenant(
        self, user_id: UUID, request: SwitchTenantRequest
    ) -> SwitchTenantResponse:
        membership = await self._tenancy_repo.get_tenant_user(
            request.tenant_id, user_id
        )
        if not membership or membership.membership_status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not an active member of this organization",
            )

        tenant = await self._tenancy_repo.get_tenant_by_id(request.tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        roles = await self._tenancy_repo.get_user_role_codes(tenant.id, user_id)
        token = create_access_token(
            user_id=user_id,
            tenant_id=tenant.id,
            roles=roles,
        )

        memberships = await self.get_user_memberships(user_id)

        return SwitchTenantResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            tenant_id=tenant.id,
            user_id=user_id,
            memberships=memberships,
        )

    # ── Invitation Flow ────────────────────────────────────────────────────────

    async def invite_user(
        self,
        request: InviteRequest,
        invited_by_user_id: UUID,
        *,
        actor_user_id: UUID | None = None,
    ) -> InviteResponse:
        # Verify target tenant exists first
        tenant = await self._tenancy_repo.get_tenant_by_id(request.tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        # Verify inviter is an admin of the target tenant
        inviter_roles = await self._tenancy_repo.get_user_role_codes(
            request.tenant_id, invited_by_user_id
        )
        if "admin" not in inviter_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can invite users",
            )

        # Verify the role exists in this tenant
        role = await self._tenancy_repo.get_role_by_code(
            request.tenant_id, request.role_code
        )
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{request.role_code}' does not exist in this organization",
            )

        # Check for existing active membership
        existing_user = await self._user_repo.get_by_email(request.email)
        if existing_user:
            existing_membership = await self._tenancy_repo.get_tenant_user(
                request.tenant_id, existing_user.id
            )
            if existing_membership and existing_membership.membership_status == "active":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This user is already an active member of the organization",
                )

        # Check for existing pending invitation
        pending = await self._invitation_repo.get_pending_by_email_and_tenant(
            request.email, request.tenant_id
        )
        if pending:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A pending invitation already exists for this email",
            )

        raw_token = generate_token()
        token_hash_value = hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        invitation = await self._invitation_repo.create(
            tenant_id=request.tenant_id,
            email=request.email,
            role_code=request.role_code,
            invited_by_user_id=invited_by_user_id,
            token_hash=token_hash_value,
            expires_at=expires_at,
        )
        await self._audit.record_event(
            tenant_id=request.tenant_id,
            actor_user_id=actor_user_id,
            action="invite_created",
            entity_type="invitation",
            entity_id=invitation.id,
            module_key="identity",
            details={
                "email": request.email,
                "role_code": request.role_code,
                "status": invitation.status,
            },
        )
        await self._db.commit()

        return InviteResponse(
            invitation_id=invitation.id,
            email=invitation.email,
            role_code=invitation.role_code,
            status=invitation.status,
            expires_at=invitation.expires_at,
            invite_token=raw_token,
        )

    async def accept_invite(
        self,
        request: AcceptInviteRequest,
        *,
        actor_user_id: UUID | None = None,
    ) -> AcceptInviteResponse:
        token_hash_value = hash_token(request.token)
        invitation = await self._invitation_repo.get_by_token_hash(token_hash_value)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid invitation token",
            )

        if invitation.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invitation is already {invitation.status}",
            )

        if datetime.now(timezone.utc) > _ensure_aware(invitation.expires_at):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation has expired",
            )

        # Find or create the user
        user = await self._user_repo.get_by_email(invitation.email)
        if not user:
            user = await self._user_repo.create(
                email=invitation.email,
                password_hash=hash_password(request.password),
                display_name=request.display_name,
            )
        else:
            # Existing user — verify password meets policy
            if not verify_password(request.password, user.password_hash):
                await self._user_repo.update_password(
                    user.id, hash_password(request.password)
                )

        # Create or activate tenant membership
        existing_membership = await self._tenancy_repo.get_tenant_user(
            invitation.tenant_id, user.id
        )
        if existing_membership:
            if existing_membership.membership_status == "active":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User is already an active member",
                )
            # Reactivate inactive membership
            existing_membership.membership_status = "active"
        else:
            await self._tenancy_repo.create_tenant_user(
                tenant_id=invitation.tenant_id,
                user_id=user.id,
                profile_type=invitation.role_code,
            )

        # Assign role
        role = await self._tenancy_repo.get_role_by_code(
            invitation.tenant_id, invitation.role_code
        )
        if role:
            await self._tenancy_repo.assign_role_to_user(
                invitation.tenant_id, user.id, role.id
            )

        # Mark invitation as accepted
        await self._invitation_repo.mark_accepted(invitation.id, user.id)
        await self._audit.record_event(
            tenant_id=invitation.tenant_id,
            actor_user_id=user.id if actor_user_id is None else actor_user_id,
            action="invite_accepted",
            entity_type="invitation",
            entity_id=invitation.id,
            module_key="identity",
            details={
                "email": invitation.email,
                "role_code": invitation.role_code,
                "accepted_by_user_id": user.id,
            },
        )
        await self._db.commit()

        # Issue JWT
        roles = await self._tenancy_repo.get_user_role_codes(
            invitation.tenant_id, user.id
        )
        token = create_access_token(
            user_id=user.id,
            tenant_id=invitation.tenant_id,
            roles=roles,
        )

        return AcceptInviteResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            tenant_id=invitation.tenant_id,
            user_id=user.id,
        )

    async def list_invitations(
        self, tenant_id: UUID, requesting_user_id: UUID
    ) -> list[InvitationStatusResponse]:
        roles = await self._tenancy_repo.get_user_role_codes(
            tenant_id, requesting_user_id
        )
        if "admin" not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view invitations",
            )
        invitations = await self._invitation_repo.get_by_tenant(tenant_id)
        return [
            InvitationStatusResponse.model_validate(inv) for inv in invitations
        ]

    async def cancel_invitation(
        self,
        invitation_id: UUID,
        tenant_id: UUID,
        requesting_user_id: UUID,
        *,
        actor_user_id: UUID | None = None,
    ) -> None:
        roles = await self._tenancy_repo.get_user_role_codes(
            tenant_id, requesting_user_id
        )
        if "admin" not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can cancel invitations",
            )
        invitation = await self._invitation_repo.get_by_id(invitation_id)
        if not invitation or invitation.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )
        if invitation.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel invitation with status '{invitation.status}'",
            )
        await self._invitation_repo.mark_cancelled(invitation_id)
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="invite_cancelled",
            entity_type="invitation",
            entity_id=invitation_id,
            module_key="identity",
            details={
                "email": invitation.email,
                "role_code": invitation.role_code,
            },
        )
        await self._db.commit()

    # ── Password Reset ─────────────────────────────────────────────────────────

    async def forgot_password(
        self, request: ForgotPasswordRequest
    ) -> ForgotPasswordResponse:
        user = await self._user_repo.get_by_email(request.email)
        if not user:
            return ForgotPasswordResponse(
                message="If the email exists, a reset token has been generated",
                reset_token=None,
            )

        # Invalidate any existing reset tokens for this user
        await self._password_reset_repo.invalidate_all_for_user(user.id)

        raw_token = generate_token()
        token_hash_value = hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        await self._password_reset_repo.create(
            user_id=user.id,
            token_hash=token_hash_value,
            expires_at=expires_at,
        )
        await self._db.commit()

        return ForgotPasswordResponse(
            message="If the email exists, a reset token has been generated",
            reset_token=raw_token,
        )

    async def reset_password(
        self, request: ResetPasswordRequest
    ) -> ResetPasswordResponse:
        token_hash_value = hash_token(request.token)
        prt = await self._password_reset_repo.get_by_token_hash(token_hash_value)
        if not prt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid reset token",
            )

        if prt.used_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has already been used",
            )

        if datetime.now(timezone.utc) > _ensure_aware(prt.expires_at):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired",
            )

        await self._user_repo.update_password(
            prt.user_id, hash_password(request.new_password)
        )
        await self._password_reset_repo.mark_used(prt.id)
        await self._db.commit()

        return ResetPasswordResponse()

    # ── MFA ────────────────────────────────────────────────────────────────────

    async def enroll_mfa(
        self, user_id: UUID, user_email: str
    ) -> MfaEnrollResponse:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        if user.totp_enabled:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="MFA is already enabled",
            )

        secret = generate_totp_secret()
        await self._user_repo.set_totp_secret(user_id, secret)

        uri = get_totp_uri(secret, user_email)

        return MfaEnrollResponse(
            secret=secret,
            uri=uri,
        )

    async def verify_and_enable_mfa(
        self,
        user_id: UUID,
        request: MfaVerifyRequest,
        *,
        tenant_id: UUID | None = None,
    ) -> MfaVerifyResponse:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        if not user.totp_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No TOTP secret configured. Enroll first.",
            )
        if user.totp_enabled:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="MFA is already enabled",
            )
        if not verify_totp(user.totp_secret, request.code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid TOTP code",
            )

        await self._user_repo.enable_totp(user_id)
        if tenant_id is not None:
            await self._audit.record_event(
                tenant_id=tenant_id,
                actor_user_id=user_id,
                action="mfa_enabled",
                entity_type="mfa",
                entity_id=user_id,
                module_key="identity",
                details={"user_id": user_id},
            )
        await self._db.commit()
        return MfaVerifyResponse()

    async def disable_mfa(
        self,
        user_id: UUID,
        *,
        tenant_id: UUID | None = None,
    ) -> None:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        await self._user_repo.disable_totp(user_id)
        if tenant_id is not None:
            await self._audit.record_event(
                tenant_id=tenant_id,
                actor_user_id=user_id,
                action="mfa_disabled",
                entity_type="mfa",
                entity_id=user_id,
                module_key="identity",
                details={"user_id": user_id},
            )
        await self._db.commit()

    # ── Token Refresh ──────────────────────────────────────────────────────────

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
        except (jwt.PyJWTError, ValueError, KeyError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

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

        tenant = await self._tenancy_repo.get_tenant_by_id(memberships[0].tenant_id)
        roles = await self._tenancy_repo.get_user_role_codes(tenant.id, user_id)
        new_access = create_access_token(
            user_id=user_id,
            tenant_id=tenant.id,
            roles=roles,
        )

        return RefreshTokenResponse(
            access_token=new_access,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )
