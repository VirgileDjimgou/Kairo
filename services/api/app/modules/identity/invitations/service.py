from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status

from app.core.capabilities import (
    CAP_MEMBERSHIP_INVITE,
    CAP_ROLE_ASSIGN,
    has_capability,
)
from app.core.config import settings
from app.core.security import (
    generate_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.modules.identity.base import IdentityServiceBase, _ensure_aware
from app.modules.identity.schemas import (
    AcceptInviteRequest,
    AcceptInviteResponse,
    InvitationStatusResponse,
    InviteRequest,
    InviteResponse,
)
from app.modules.tenancy.branding import branding_from_json


class InvitationsMixin(IdentityServiceBase):
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

        # President and secretary general may invite ordinary members without
        # receiving broad role-management or lifecycle permissions.
        inviter_roles = await self._tenancy_repo.get_user_role_codes(
            request.tenant_id, invited_by_user_id
        )
        can_assign_any_role = has_capability(inviter_roles, CAP_ROLE_ASSIGN)
        can_invite_member = (
            request.role_code == "member"
            and has_capability(inviter_roles, CAP_MEMBERSHIP_INVITE)
        )
        if not (can_assign_any_role or can_invite_member):
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
        expires_at = datetime.now(UTC) + timedelta(days=7)

        invitation = await self._invitation_repo.create(
            tenant_id=request.tenant_id,
            email=request.email,
            role_code=request.role_code,
            invited_by_user_id=invited_by_user_id,
            token_hash=token_hash_value,
            expires_at=expires_at,
        )
        branding = branding_from_json(tenant.branding_json)
        delivery = await self._send_identity_email(
            tenant_id=request.tenant_id,
            recipient=request.email,
            subject=f"You're invited to join {tenant.name} on {branding.notification_name or settings.app_name}",
            body=self._build_invitation_message(
                tenant_name=tenant.name,
                role_code=request.role_code,
                raw_token=raw_token,
                notification_name=branding.notification_name or settings.app_name,
                support_name=branding.support_name,
                support_email=branding.support_email,
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

        if datetime.now(UTC) > _ensure_aware(invitation.expires_at):
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
    def _build_invitation_message(
        self,
        *,
        tenant_name: str,
        role_code: str,
        raw_token: str,
        notification_name: str | None = None,
        support_name: str = "",
        support_email: str = "",
    ) -> str:
        sender = notification_name or settings.app_name
        support_line = (
            f"\n\nNeed help? Contact {support_name or sender} at {support_email}."
            if support_email
            else ""
        )
        return (
            f"{sender} access invitation\n\n"
            f"You have been invited to join {tenant_name} as {role_code}.\n\n"
            "Use this secure invitation link:\n"
            f"/accept-invite?token={raw_token}\n\n"
            "If you were not expecting this invitation, ignore this message."
            f"{support_line}"
        )
