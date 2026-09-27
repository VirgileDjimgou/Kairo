from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Self
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.capabilities import (
    CAP_ROLE_ASSIGN,
    has_capability,
)
from app.core.security import (
    create_access_token,
)
from app.modules.audit.service import AuditService
from app.modules.identity.repository import (
    InvitationRepository,
    PasswordResetRepository,
    UserRepository,
    UserSessionRepository,
)
from app.modules.tenancy.repository import TenancyRepository
from app.providers.notifications.base import NotificationDispatchResult, NotificationProvider

SUPPORTED_INTERFACE_LANGUAGES = {"fr", "en", "de"}
ASSISTED_ACCESS_RECOVERY_TTL_HOURS = 48
_RECOVERY_PASSWORD_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
def _ensure_aware(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware (assume UTC if naive)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt

class IdentityServiceBase:
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
    ) -> Self:
        self._notification_providers = providers
        return self
    def with_request_context(
        self,
        *,
        ip_address: str | None,
        user_agent: str | None,
    ) -> Self:
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
    async def _record_session_revocation_events(
        self,
        *,
        tenant_id: UUID,
        actor_user_id: UUID,
        revoked_sessions: Sequence[object],
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
    async def _first_tenant_id_for_user(self, user_id: UUID) -> UUID | None:
        memberships = await self._tenancy_repo.get_user_active_memberships(user_id)
        if memberships:
            return memberships[0].tenant_id
        return None
