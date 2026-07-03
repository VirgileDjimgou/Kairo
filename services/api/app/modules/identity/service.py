import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.capabilities import CAP_ROLE_ASSIGN, has_capability
from app.core.config import settings
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
from app.modules.audit.service import AuditService
from app.modules.identity.repository import (
    InvitationRepository,
    PasswordResetRepository,
    UserRepository,
    UserSessionRepository,
)
from app.modules.identity.schemas import (
    AcceptInviteRequest,
    AcceptInviteResponse,
    ActiveSessionResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    InvitationStatusResponse,
    InviteRequest,
    InviteResponse,
    LoginRequest,
    ManagedTenantUserActionResponse,
    ManagedTenantUserRolesUpdateRequest,
    ManagedTenantUserRolesUpdateResponse,
    ManagedTenantUserResponse,
    MfaCompleteLoginRequest,
    MfaEnrollResponse,
    MfaLoginResponse,
    MfaRequiredResponse,
    MfaStatusResponse,
    MfaVerifyRequest,
    MfaVerifyResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SecurityEventResponse,
    SessionActionResponse,
    SwitchTenantRequest,
    SwitchTenantResponse,
    TenantMembershipResponse,
    TokenResponse,
)
from app.modules.tenancy.module_toggles import parse_module_toggles
from app.modules.tenancy.repository import TenancyRepository
from app.modules.tenancy.schemas import BrandingConfig, ModuleToggles
from app.providers.notifications.base import NotificationDispatchResult, NotificationProvider


def _ensure_aware(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware (assume UTC if naive)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


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
        self._session_repo = UserSessionRepository(db)
        self._audit = AuditService(db)
        self._notification_providers: list[NotificationProvider] = []
        self._request_ip: str | None = None
        self._request_user_agent: str | None = None

    def with_notification_providers(
        self, providers: list[NotificationProvider]
    ) -> "AuthService":
        self._notification_providers = providers
        return self

    def with_request_context(
        self,
        *,
        ip_address: str | None,
        user_agent: str | None,
    ) -> "AuthService":
        self._request_ip = ip_address
        self._request_user_agent = user_agent
        return self

    async def _require_admin(self, tenant_id: UUID, user_id: UUID) -> list[str]:
        roles = await self._tenancy_repo.get_user_role_codes(tenant_id, user_id)
        if not has_capability(roles, CAP_ROLE_ASSIGN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only authorized tenant administrators can perform this action",
            )
        return roles

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
        self,
        user_id: UUID,
        request: SwitchTenantRequest,
        *,
        session_id: UUID,
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
        await self._session_repo.touch(
            session_id,
            tenant_id=tenant.id,
            ip_address=self._request_ip,
            user_agent=self._request_user_agent,
        )
        token = create_access_token(
            user_id=user_id,
            tenant_id=tenant.id,
            roles=roles,
            session_id=session_id,
        )

        memberships = await self.get_user_memberships(user_id)
        await self._db.commit()

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
        if not has_capability(inviter_roles, CAP_ROLE_ASSIGN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only authorized tenant administrators can invite users",
            )

        await self._tenancy_repo.ensure_canonical_role_catalog(request.tenant_id)
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
            if existing_membership:
                if existing_membership.membership_status == "active":
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="This user is already an active member of the organization",
                    )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "This user already has access history in the organization. "
                        "Use lifecycle controls to reactivate or manage the account."
                    ),
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
        delivery = await self._send_identity_email(
            tenant_id=request.tenant_id,
            recipient=request.email,
            subject=f"You're invited to join {tenant.name} on {settings.app_name}",
            body=self._build_invitation_message(
                tenant_name=tenant.name,
                role_code=request.role_code,
                raw_token=raw_token,
            ),
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
                "delivery_status": delivery.status,
                "delivery_simulation_only": delivery.simulation_only,
            },
        )
        await self._db.commit()

        return InviteResponse(
            invitation_id=invitation.id,
            email=invitation.email,
            role_code=invitation.role_code,
            status=invitation.status,
            expires_at=invitation.expires_at,
            delivery_status=delivery.status,
            delivery_message=delivery.message,
            delivery_simulation_only=delivery.simulation_only,
            invite_token=(
                raw_token
                if delivery.simulation_only or not delivery.delivered or settings.app_env == "development"
                else None
            ),
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
        membership = await self._tenancy_repo.get_tenant_user(
            invitation.tenant_id, user.id
        )
        if membership:
            if membership.membership_status == "active":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User is already an active member",
                )
            if membership.membership_status == "suspended":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This membership is suspended. Ask an administrator to reactivate access.",
                )
            # Reactivate inactive membership
            membership.membership_status = "active"
        else:
            membership = await self._tenancy_repo.create_tenant_user(
                tenant_id=invitation.tenant_id,
                user_id=user.id,
                profile_type=invitation.role_code,
            )

        # Assign role
        await self._tenancy_repo.ensure_canonical_role_catalog(invitation.tenant_id)
        role = await self._tenancy_repo.get_role_by_code(
            invitation.tenant_id, invitation.role_code
        )
        if role:
            await self._tenancy_repo.assign_role_to_user(
                invitation.tenant_id, user.id, role.id
            )
            await self._audit.record_event(
                tenant_id=invitation.tenant_id,
                actor_user_id=user.id if actor_user_id is None else actor_user_id,
                action="role_assigned",
                entity_type="tenant_user",
                entity_id=membership.id if membership is not None else None,
                module_key="identity",
                details={
                    "assigned_user_id": user.id,
                    "role_code": invitation.role_code,
                    "source": "invitation_acceptance",
                },
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
        token, session_id = await self._issue_session_access_token(
            user_id=user.id,
            tenant_id=invitation.tenant_id,
            roles=roles,
        )
        await self._audit.record_event(
            tenant_id=invitation.tenant_id,
            actor_user_id=user.id,
            action="login_succeeded",
            entity_type="session",
            entity_id=session_id,
            module_key="identity",
            details={
                "tenant_id": invitation.tenant_id,
                "mfa_completed": False,
                "source": "accept_invite",
            },
        )
        await self._db.commit()

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
        await self._require_admin(tenant_id, requesting_user_id)
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
        await self._require_admin(tenant_id, requesting_user_id)
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

    async def list_managed_users(
        self,
        *,
        tenant_id: UUID,
        requesting_user_id: UUID,
    ) -> list[ManagedTenantUserResponse]:
        await self._require_admin(tenant_id, requesting_user_id)
        rows = await self._tenancy_repo.list_tenant_user_details(tenant_id)
        user_ids = [user.id for _, user in rows]
        session_counts = await self._session_repo.count_active_for_users_by_tenant(
            tenant_id=tenant_id,
            user_ids=user_ids,
        )
        latest_events = await self._latest_identity_events_for_users(
            tenant_id=tenant_id,
            user_ids=user_ids,
        )
        result: list[ManagedTenantUserResponse] = []
        for membership, user in rows:
            roles = await self._tenancy_repo.get_user_role_codes(tenant_id, user.id)
            latest_event = latest_events.get(user.id)
            result.append(
                ManagedTenantUserResponse(
                    user_id=user.id,
                    email=user.email,
                    display_name=user.display_name,
                    profile_type=membership.profile_type,
                    membership_status=membership.membership_status,
                    user_status=user.status,
                    roles=roles,
                    last_login_at=user.last_login_at,
                    active_session_count=session_counts.get(user.id, 0),
                    last_security_event_action=(
                        latest_event.action if latest_event is not None else None
                    ),
                    last_security_event_at=(
                        latest_event.created_at if latest_event is not None else None
                    ),
                )
            )
        return result

    async def suspend_tenant_user(
        self,
        *,
        tenant_id: UUID,
        target_user_id: UUID,
        requesting_user_id: UUID,
        actor_user_id: UUID | None = None,
    ) -> ManagedTenantUserActionResponse:
        await self._require_admin(tenant_id, requesting_user_id)
        if target_user_id == requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use a different administrator to suspend this account.",
            )
        membership = await self._tenancy_repo.get_tenant_user(tenant_id, target_user_id)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Managed user not found",
            )
        previous_status = membership.membership_status
        if previous_status == "suspended":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This tenant user is already suspended",
            )
        updated_membership = await self._tenancy_repo.update_membership_status(
            tenant_id,
            target_user_id,
            "suspended",
        )
        revoked_sessions = await self._session_repo.revoke_all_for_user_and_tenant(
            user_id=target_user_id,
            tenant_id=tenant_id,
            revoked_reason="admin_suspended_membership",
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="tenant_user_suspended",
            entity_type="tenant_user",
            entity_id=membership.id,
            module_key="identity",
            details={
                "user_id": target_user_id,
                "previous_status": previous_status,
                "new_status": "suspended",
                "revoked_session_count": len(revoked_sessions),
            },
        )
        await self._record_session_revocation_events(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id or requesting_user_id,
            revoked_sessions=revoked_sessions,
            reason="admin_suspended_membership",
        )
        await self._db.commit()
        return ManagedTenantUserActionResponse(
            message="The tenant user has been suspended and active tenant sessions were revoked.",
            membership_status=(
                updated_membership.membership_status
                if updated_membership is not None
                else "suspended"
            ),
            revoked_session_count=len(revoked_sessions),
        )

    async def reactivate_tenant_user(
        self,
        *,
        tenant_id: UUID,
        target_user_id: UUID,
        requesting_user_id: UUID,
        actor_user_id: UUID | None = None,
    ) -> ManagedTenantUserActionResponse:
        await self._require_admin(tenant_id, requesting_user_id)
        membership = await self._tenancy_repo.get_tenant_user(tenant_id, target_user_id)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Managed user not found",
            )
        previous_status = membership.membership_status
        if previous_status == "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This tenant user is already active",
            )
        updated_membership = await self._tenancy_repo.update_membership_status(
            tenant_id,
            target_user_id,
            "active",
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="tenant_user_reactivated",
            entity_type="tenant_user",
            entity_id=membership.id,
            module_key="identity",
            details={
                "user_id": target_user_id,
                "previous_status": previous_status,
                "new_status": "active",
            },
        )
        await self._db.commit()
        return ManagedTenantUserActionResponse(
            message="The tenant user has been reactivated.",
            membership_status=(
                updated_membership.membership_status
                if updated_membership is not None
                else "active"
            ),
            revoked_session_count=0,
        )

    async def revoke_tenant_user_sessions(
        self,
        *,
        tenant_id: UUID,
        target_user_id: UUID,
        requesting_user_id: UUID,
        actor_user_id: UUID | None = None,
    ) -> ManagedTenantUserActionResponse:
        await self._require_admin(tenant_id, requesting_user_id)
        if target_user_id == requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use account security to revoke your own sessions.",
            )
        membership = await self._tenancy_repo.get_tenant_user(tenant_id, target_user_id)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Managed user not found",
            )
        revoked_sessions = await self._session_repo.revoke_all_for_user_and_tenant(
            user_id=target_user_id,
            tenant_id=tenant_id,
            revoked_reason="admin_forced_tenant_revocation",
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="tenant_user_sessions_revoked",
            entity_type="tenant_user",
            entity_id=membership.id,
            module_key="identity",
            details={
                "user_id": target_user_id,
                "revoked_session_count": len(revoked_sessions),
            },
        )
        await self._record_session_revocation_events(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id or requesting_user_id,
            revoked_sessions=revoked_sessions,
            reason="admin_forced_tenant_revocation",
        )
        await self._db.commit()
        return ManagedTenantUserActionResponse(
            message="Active tenant sessions were revoked for the managed user.",
            membership_status=membership.membership_status,
            revoked_session_count=len(revoked_sessions),
        )

    async def update_tenant_user_roles(
        self,
        *,
        tenant_id: UUID,
        target_user_id: UUID,
        requesting_user_id: UUID,
        request: ManagedTenantUserRolesUpdateRequest,
        actor_user_id: UUID | None = None,
    ) -> ManagedTenantUserRolesUpdateResponse:
        await self._require_admin(tenant_id, requesting_user_id)
        if target_user_id == requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use another administrator account to modify your own roles.",
            )

        await self._tenancy_repo.ensure_canonical_role_catalog(tenant_id)
        membership = await self._tenancy_repo.get_tenant_user(tenant_id, target_user_id)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Managed user not found in this organization",
            )

        normalized_role_codes = list(dict.fromkeys(request.role_codes))
        resolved_roles = []
        for role_code in normalized_role_codes:
            role = await self._tenancy_repo.get_role_by_code(tenant_id, role_code)
            if role is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role '{role_code}' does not exist in this organization",
                )
            resolved_roles.append(role)

        previous_roles, updated_roles = await self._tenancy_repo.replace_user_roles(
            tenant_id=tenant_id,
            user_id=target_user_id,
            role_ids=[role.id for role in resolved_roles],
        )
        previous_role_codes = sorted(role.code for role in previous_roles)
        updated_role_codes = sorted(role.code for role in updated_roles)

        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=requesting_user_id if actor_user_id is None else actor_user_id,
            action="roles_updated",
            entity_type="tenant_user",
            entity_id=membership.id,
            module_key="identity",
            details={
                "target_user_id": target_user_id,
                "previous_role_codes": previous_role_codes,
                "role_codes": updated_role_codes,
                "added_role_codes": sorted(set(updated_role_codes) - set(previous_role_codes)),
                "removed_role_codes": sorted(set(previous_role_codes) - set(updated_role_codes)),
            },
        )
        await self._db.commit()

        return ManagedTenantUserRolesUpdateResponse(
            message="Tenant roles updated successfully.",
            role_codes=updated_role_codes,
        )

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
        tenant_id = await self._first_tenant_id_for_user(user.id)
        delivery = await self._send_identity_email(
            tenant_id=tenant_id if tenant_id is not None else UUID(int=0),
            recipient=user.email,
            subject=f"Reset your {settings.app_name} password",
            body=self._build_password_reset_message(raw_token=raw_token),
        )
        tenant_id = await self._first_tenant_id_for_user(user.id)
        if tenant_id is not None:
            await self._audit.record_event(
                tenant_id=tenant_id,
                actor_user_id=user.id,
                action="password_reset_requested",
                entity_type="password_reset",
                entity_id=user.id,
                module_key="identity",
                details={
                    "email": user.email,
                    "delivery_status": delivery.status,
                    "delivery_simulation_only": delivery.simulation_only,
                },
            )
        await self._db.commit()

        return ForgotPasswordResponse(
            message="If the email exists, a reset token has been generated",
            reset_token=(
                raw_token
                if delivery.simulation_only or settings.app_env == "development"
                else None
            ),
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
        revoked_sessions = await self._session_repo.revoke_all_for_user(
            user_id=prt.user_id,
            revoked_reason="password_reset",
        )
        tenant_id = await self._first_tenant_id_for_user(prt.user_id)
        if tenant_id is not None:
            await self._audit.record_event(
                tenant_id=tenant_id,
                actor_user_id=prt.user_id,
                action="password_reset_completed",
                entity_type="password_reset",
                entity_id=prt.id,
                module_key="identity",
                details={
                    "revoked_session_count": len(revoked_sessions),
                },
            )
            await self._record_session_revocation_events(
                tenant_id=tenant_id,
                actor_user_id=prt.user_id,
                revoked_sessions=revoked_sessions,
                reason="password_reset",
            )
        await self._db.commit()

        return ResetPasswordResponse()

    async def list_active_sessions(
        self,
        *,
        user_id: UUID,
        current_session_id: UUID,
    ) -> list[ActiveSessionResponse]:
        sessions = await self._session_repo.list_active_for_user(user_id)
        return [
            ActiveSessionResponse(
                id=session.id,
                current=session.id == current_session_id,
                current_tenant_id=session.current_tenant_id,
                created_at=session.created_at,
                last_seen_at=session.last_seen_at,
                created_ip=session.created_ip,
                last_seen_ip=session.last_seen_ip,
                created_user_agent=session.created_user_agent,
                last_seen_user_agent=session.last_seen_user_agent,
            )
            for session in sessions
        ]

    async def revoke_other_sessions(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
        current_session_id: UUID,
    ) -> SessionActionResponse:
        revoked_sessions = await self._session_repo.revoke_other_sessions(
            user_id=user_id,
            keep_session_id=current_session_id,
            revoked_reason="manual_revoke_others",
        )
        await self._record_session_revocation_events(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            revoked_sessions=revoked_sessions,
            reason="manual_revoke_others",
        )
        await self._db.commit()
        return SessionActionResponse(
            message="Other active sessions have been revoked.",
            revoked_session_count=len(revoked_sessions),
        )

    async def revoke_all_sessions(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
    ) -> SessionActionResponse:
        revoked_sessions = await self._session_repo.revoke_all_for_user(
            user_id=user_id,
            revoked_reason="manual_revoke_all",
        )
        await self._record_session_revocation_events(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            revoked_sessions=revoked_sessions,
            reason="manual_revoke_all",
        )
        await self._db.commit()
        return SessionActionResponse(
            message="All active sessions have been revoked.",
            revoked_session_count=len(revoked_sessions),
        )

    async def revoke_session(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
        current_session_id: UUID,
        target_session_id: UUID,
    ) -> SessionActionResponse:
        if target_session_id == current_session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use the revoke-all action to end the current session.",
            )
        session = await self._session_repo.get_active_by_id(target_session_id)
        if session is None or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        revoked = await self._session_repo.revoke_session(
            session_id=target_session_id,
            revoked_reason="manual_revoke_session",
        )
        await self._record_session_revocation_events(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            revoked_sessions=[revoked] if revoked is not None else [],
            reason="manual_revoke_session",
        )
        await self._db.commit()
        return SessionActionResponse(
            message="The selected session has been revoked.",
            revoked_session_count=1 if revoked is not None else 0,
        )

    async def list_security_events(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
        limit: int = 20,
    ) -> list[SecurityEventResponse]:
        allowed_actions = {
            "login_succeeded",
            "mfa_enabled",
            "mfa_disabled",
            "password_reset_requested",
            "password_reset_completed",
            "session_revoked",
        }
        events = await self._audit.list_events(
            tenant_id,
            limit=limit * 2,
            offset=0,
            module_key="identity",
        )
        result: list[SecurityEventResponse] = []
        for event in events:
            if event.action not in allowed_actions:
                continue
            if event.actor_user_id != user_id and event.entity_id != str(user_id):
                continue
            result.append(
                SecurityEventResponse(
                    id=event.id,
                    action=event.action,
                    actor_user_id=event.actor_user_id,
                    entity_type=event.entity_type,
                    entity_id=event.entity_id,
                    details=event.details,
                    created_at=event.created_at,
                )
            )
            if len(result) >= limit:
                break
        return result

    async def _send_identity_email(
        self,
        *,
        tenant_id: UUID,
        recipient: str,
        subject: str,
        body: str,
    ) -> NotificationDispatchResult:
        provider = next(
            (item for item in self._notification_providers if getattr(item, "channel", "") == "email"),
            None,
        )
        if provider is None:
            return NotificationDispatchResult(
                channel="email",
                status="manual",
                message="No email provider is available. Manual or development fallback remains active.",
                delivered=False,
                simulation_only=True,
            )

        return await provider.send_message(
            tenant_id=tenant_id,
            actor_user_id=None,
            recipient=recipient,
            subject=subject,
            body=body,
        )

    async def _first_tenant_id_for_user(self, user_id: UUID) -> UUID | None:
        memberships = await self._tenancy_repo.get_user_active_memberships(user_id)
        if memberships:
            return memberships[0].tenant_id
        return None

    async def _latest_identity_events_for_users(
        self,
        *,
        tenant_id: UUID,
        user_ids: list[UUID],
    ) -> dict[UUID, SecurityEventResponse]:
        if not user_ids:
            return {}
        user_id_set = set(user_ids)
        events = await self._audit.list_events(
            tenant_id,
            limit=max(100, len(user_ids) * 6),
            offset=0,
            module_key="identity",
        )
        latest: dict[UUID, SecurityEventResponse] = {}
        for event in events:
            target_user_id = self._resolve_identity_event_user_id(event)
            if target_user_id is None or target_user_id not in user_id_set:
                continue
            if target_user_id in latest:
                continue
            latest[target_user_id] = event
        return latest

    def _resolve_identity_event_user_id(
        self,
        event: SecurityEventResponse,
    ) -> UUID | None:
        details = event.details if isinstance(event.details, dict) else {}
        if event.actor_user_id is not None:
            return event.actor_user_id
        details_user_id = details.get("user_id") or details.get("session_user_id")
        if details_user_id:
            try:
                return UUID(str(details_user_id))
            except ValueError:
                return None
        if event.entity_type in {"mfa", "password_reset"} and event.entity_id:
            try:
                return UUID(str(event.entity_id))
            except ValueError:
                return None
        return None

    async def _issue_session_access_token(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
        roles: list[str],
    ) -> tuple[str, UUID]:
        session = await self._session_repo.create(
            user_id=user_id,
            tenant_id=tenant_id,
            ip_address=self._request_ip,
            user_agent=self._request_user_agent,
        )
        return (
            create_access_token(
                user_id=user_id,
                tenant_id=tenant_id,
                roles=roles,
                session_id=session.id,
            ),
            session.id,
        )

    async def _record_session_revocation_events(
        self,
        *,
        tenant_id: UUID,
        actor_user_id: UUID,
        revoked_sessions: list[object],
        reason: str,
    ) -> None:
        for session in revoked_sessions:
            await self._audit.record_event(
                tenant_id=tenant_id,
                actor_user_id=actor_user_id,
                action="session_revoked",
                entity_type="session",
                entity_id=getattr(session, "id", None),
                module_key="identity",
                details={
                    "reason": reason,
                    "session_user_id": getattr(session, "user_id", None),
                    "tenant_id": getattr(session, "current_tenant_id", None),
                },
            )

    def _build_invitation_message(
        self,
        *,
        tenant_name: str,
        role_code: str,
        raw_token: str,
    ) -> str:
        return (
            f"{settings.app_name} access invitation\n\n"
            f"You have been invited to join {tenant_name} as {role_code}.\n\n"
            "Use this secure invitation link:\n"
            f"/accept-invite?token={raw_token}\n\n"
            "If you were not expecting this invitation, ignore this message."
        )

    def _build_password_reset_message(self, *, raw_token: str) -> str:
        return (
            f"{settings.app_name} password reset\n\n"
            f"A password reset was requested for your {settings.app_name} account.\n\n"
            "Use this secure reset link:\n"
            f"/reset-password?token={raw_token}\n\n"
            "If you did not request this, you can ignore this email."
        )

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

    async def get_mfa_status(self, user_id: UUID) -> MfaStatusResponse:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return MfaStatusResponse(
            enabled=bool(user.totp_enabled),
            enrolled=bool(user.totp_secret),
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
        current_session_id: UUID | None = None,
    ) -> None:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        await self._user_repo.disable_totp(user_id)
        revoked_sessions = (
            await self._session_repo.revoke_other_sessions(
                user_id=user_id,
                keep_session_id=current_session_id,
                revoked_reason="mfa_disabled",
            )
            if current_session_id is not None
            else await self._session_repo.revoke_all_for_user(
                user_id=user_id,
                revoked_reason="mfa_disabled",
            )
        )
        if tenant_id is not None:
            await self._audit.record_event(
                tenant_id=tenant_id,
                actor_user_id=user_id,
                action="mfa_disabled",
                entity_type="mfa",
                entity_id=user_id,
                module_key="identity",
                details={
                    "user_id": user_id,
                    "revoked_session_count": len(revoked_sessions),
                },
            )
            await self._record_session_revocation_events(
                tenant_id=tenant_id,
                actor_user_id=user_id,
                revoked_sessions=revoked_sessions,
                reason="mfa_disabled",
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
            session_id = UUID(payload["sid"])
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
