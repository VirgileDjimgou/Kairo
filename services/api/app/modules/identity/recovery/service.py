import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status

from app.core.capabilities import (
    CAP_IDENTITY_ACCESS_RECOVERY,
    has_capability,
)
from app.core.security import (
    hash_password,
)
from app.modules.identity.base import (
    _RECOVERY_PASSWORD_ALPHABET,
    ASSISTED_ACCESS_RECOVERY_TTL_HOURS,
    IdentityServiceBase,
)
from app.modules.identity.schemas import (
    AssistedAccessRecoveryRequest,
    AssistedAccessRecoveryResponse,
)


class RecoveryMixin(IdentityServiceBase):
    async def recover_member_access(
        self,
        *,
        tenant_id: UUID,
        requesting_user_id: UUID,
        target_user_id: UUID,
        request: AssistedAccessRecoveryRequest,
    ) -> AssistedAccessRecoveryResponse:
        if requesting_user_id == target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use the account security page to change your own password",
            )
        await self._require_access_recovery_authority(tenant_id, requesting_user_id)
        membership = await self._tenancy_repo.get_tenant_user(tenant_id, target_user_id)
        if membership is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        target = await self._user_repo.get_by_id(target_user_id)
        if target is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        if target.status != "active" or membership.membership_status != "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only active members can receive temporary access",
            )

        temporary_password = self._generate_assisted_recovery_password()
        expires_at = datetime.now(UTC) + timedelta(hours=ASSISTED_ACCESS_RECOVERY_TTL_HOURS)
        await self._user_repo.update_password(
            target.id,
            hash_password(temporary_password),
            password_change_required=True,
            temporary_password_expires_at=expires_at,
        )
        await self._password_reset_repo.invalidate_all_for_user(target.id)
        revoked_sessions = await self._session_repo.revoke_all_for_user(
            user_id=target.id,
            revoked_reason="assisted_access_recovery",
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=requesting_user_id,
            action="assisted_access_recovery_issued",
            entity_type="user",
            entity_id=target.id,
            module_key="identity",
            details={
                "target_display_name": target.display_name,
                "reason": request.reason,
                "expires_at": expires_at.isoformat(),
                "revoked_session_count": len(revoked_sessions),
            },
        )
        await self._record_session_revocation_events(
            tenant_id=tenant_id,
            actor_user_id=requesting_user_id,
            revoked_sessions=revoked_sessions,
            reason="assisted_access_recovery",
        )
        await self._db.commit()
        return AssistedAccessRecoveryResponse(
            target_user_id=target.id,
            target_display_name=target.display_name,
            temporary_password=temporary_password,
            expires_at=expires_at,
            revoked_session_count=len(revoked_sessions),
        )
    async def _require_access_recovery_authority(
        self, tenant_id: UUID, user_id: UUID
    ) -> list[str]:
        roles = await self._tenancy_repo.get_user_role_codes(tenant_id, user_id)
        if not has_capability(roles, CAP_IDENTITY_ACCESS_RECOVERY):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only authorized office roles can recover another member's access",
            )
        return roles

    @staticmethod
    def _generate_assisted_recovery_password() -> str:
        groups = [
            "".join(secrets.choice(_RECOVERY_PASSWORD_ALPHABET) for _ in range(4))
            for _ in range(3)
        ]
        return f"Kairo-{'-'.join(groups)}!"
