from uuid import UUID

from fastapi import HTTPException, status

from app.core.security import (
    generate_totp_secret,
    get_totp_uri,
    verify_totp,
)
from app.modules.identity.base import IdentityServiceBase
from app.modules.identity.schemas import (
    MfaEnrollResponse,
    MfaStatusResponse,
    MfaVerifyRequest,
    MfaVerifyResponse,
)


class MfaMixin(IdentityServiceBase):
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
