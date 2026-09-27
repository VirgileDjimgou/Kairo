from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import (
    generate_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.modules.identity.base import IdentityServiceBase, _ensure_aware
from app.modules.identity.schemas import (
    ChangeInitialPasswordRequest,
    ChangeInitialPasswordResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)


class PasswordsMixin(IdentityServiceBase):
    async def change_initial_password(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
        current_session_id: UUID,
        request: ChangeInitialPasswordRequest,
    ) -> ChangeInitialPasswordResponse:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not user.password_change_required:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This account does not require an initial password change",
            )

        await self._user_repo.update_password(
            user_id,
            hash_password(request.new_password),
            password_change_required=False,
            clear_temporary_password_expiry=True,
        )
        revoked_sessions = await self._session_repo.revoke_other_sessions(
            user_id=user_id,
            keep_session_id=current_session_id,
            revoked_reason="initial_password_changed",
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            action="initial_password_changed",
            entity_type="user",
            entity_id=user_id,
            module_key="identity",
            details={"revoked_session_count": len(revoked_sessions)},
        )
        await self._record_session_revocation_events(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            revoked_sessions=revoked_sessions,
            reason="initial_password_changed",
        )
        await self._db.commit()
        return ChangeInitialPasswordResponse()
    async def change_password(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
        current_session_id: UUID,
        request: ChangePasswordRequest,
    ) -> ChangePasswordResponse:
        user = await self._user_repo.get_by_id(user_id)
        if user is None or not verify_password(request.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The current password is incorrect",
            )
        if user.password_change_required:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Use the required password change screen before changing this password again",
            )
        if request.current_password == request.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Choose a password different from the current password",
            )

        await self._user_repo.update_password(
            user_id,
            hash_password(request.new_password),
            password_change_required=False,
            clear_temporary_password_expiry=True,
        )
        revoked_sessions = await self._session_repo.revoke_other_sessions(
            user_id=user_id,
            keep_session_id=current_session_id,
            revoked_reason="password_changed",
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            action="password_changed",
            entity_type="user",
            entity_id=user_id,
            module_key="identity",
            details={"revoked_session_count": len(revoked_sessions)},
        )
        await self._record_session_revocation_events(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            revoked_sessions=revoked_sessions,
            reason="password_changed",
        )
        await self._db.commit()
        return ChangePasswordResponse(revoked_session_count=len(revoked_sessions))
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
        expires_at = datetime.now(UTC) + timedelta(hours=1)

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

        if datetime.now(UTC) > _ensure_aware(prt.expires_at):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired",
            )

        await self._user_repo.update_password(
            prt.user_id,
            hash_password(request.new_password),
            password_change_required=False,
            clear_temporary_password_expiry=True,
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
    def _build_password_reset_message(self, *, raw_token: str) -> str:
        return (
            f"{settings.app_name} password reset\n\n"
            f"A password reset was requested for your {settings.app_name} account.\n\n"
            "Use this secure reset link:\n"
            f"/reset-password?token={raw_token}\n\n"
            "If you did not request this, you can ignore this email."
        )
