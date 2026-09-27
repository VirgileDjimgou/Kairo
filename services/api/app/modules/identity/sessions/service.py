from uuid import UUID

from fastapi import HTTPException, status

from app.modules.identity.base import IdentityServiceBase
from app.modules.identity.schemas import (
    ActiveSessionResponse,
    SecurityEventResponse,
    SessionActionResponse,
)


class SessionsMixin(IdentityServiceBase):
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
