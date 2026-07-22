from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.models import Invitation, PasswordResetToken, User, UserSession


class UserRepository:
    """
    Data access for the User model.

    Note: User is NOT tenant-scoped. Tenant membership is resolved
    through TenantUserRepository. Every method here operates on the
    global users table without a tenant_id filter — this is intentional
    and correct per the data model.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self._db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self._db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        password_hash: str,
        display_name: str,
        status: str = "active",
    ) -> User:
        user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            display_name=display_name,
            status=status,
        )
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        return user

    async def update_last_login(self, user_id: UUID) -> None:
        await self._db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                last_login_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )

    async def update_password(self, user_id: UUID, new_password_hash: str) -> None:
        await self._db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                password_hash=new_password_hash,
                updated_at=datetime.now(UTC),
            )
        )

    async def update_preferred_language(self, user_id: UUID, preferred_language: str) -> None:
        await self._db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                preferred_language=preferred_language,
                updated_at=datetime.now(UTC),
            )
        )

    async def set_totp_secret(self, user_id: UUID, secret: str) -> None:
        await self._db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                totp_secret=secret,
                updated_at=datetime.now(UTC),
            )
        )

    async def enable_totp(self, user_id: UUID) -> None:
        await self._db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                totp_enabled=True,
                updated_at=datetime.now(UTC),
            )
        )

    async def disable_totp(self, user_id: UUID) -> None:
        await self._db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                totp_secret=None,
                totp_enabled=False,
                updated_at=datetime.now(UTC),
            )
        )


class UserSessionRepository:
    """Data access for persisted authenticated sessions."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, session_id: UUID) -> UserSession | None:
        result = await self._db.execute(
            select(UserSession).where(UserSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_active_by_id(self, session_id: UUID) -> UserSession | None:
        result = await self._db.execute(
            select(UserSession).where(
                UserSession.id == session_id,
                UserSession.revoked_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_active_for_user(self, user_id: UUID) -> list[UserSession]:
        result = await self._db.execute(
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.revoked_at.is_(None),
            )
            .order_by(UserSession.last_seen_at.desc(), UserSession.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_active_for_user_and_tenant(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
    ) -> list[UserSession]:
        result = await self._db.execute(
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.current_tenant_id == tenant_id,
                UserSession.revoked_at.is_(None),
            )
            .order_by(UserSession.last_seen_at.desc(), UserSession.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_active_for_users_by_tenant(
        self,
        *,
        tenant_id: UUID,
        user_ids: list[UUID],
    ) -> dict[UUID, int]:
        if not user_ids:
            return {}
        result = await self._db.execute(
            select(UserSession.user_id, func.count(UserSession.id))
            .where(
                UserSession.current_tenant_id == tenant_id,
                UserSession.user_id.in_(user_ids),
                UserSession.revoked_at.is_(None),
            )
            .group_by(UserSession.user_id)
        )
        return {user_id: int(count) for user_id, count in result.all()}

    async def create(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
        ip_address: str | None,
        user_agent: str | None,
    ) -> UserSession:
        session = UserSession(
            user_id=user_id,
            current_tenant_id=tenant_id,
            created_ip=ip_address,
            created_user_agent=user_agent,
            last_seen_ip=ip_address,
            last_seen_user_agent=user_agent,
        )
        self._db.add(session)
        await self._db.flush()
        await self._db.refresh(session)
        return session

    async def touch(
        self,
        session_id: UUID,
        *,
        tenant_id: UUID,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        await self._db.execute(
            update(UserSession)
            .where(
                UserSession.id == session_id,
                UserSession.revoked_at.is_(None),
            )
            .values(
                current_tenant_id=tenant_id,
                last_seen_at=datetime.now(UTC),
                last_seen_ip=ip_address,
                last_seen_user_agent=user_agent,
            )
        )

    async def revoke_session(
        self,
        *,
        session_id: UUID,
        revoked_reason: str,
    ) -> UserSession | None:
        session = await self.get_active_by_id(session_id)
        if session is None:
            return None
        session.revoked_at = datetime.now(UTC)
        session.revoked_reason = revoked_reason
        await self._db.flush()
        return session

    async def revoke_other_sessions(
        self,
        *,
        user_id: UUID,
        keep_session_id: UUID,
        revoked_reason: str,
    ) -> list[UserSession]:
        sessions = await self.list_active_for_user(user_id)
        revoked: list[UserSession] = []
        now = datetime.now(UTC)
        for session in sessions:
            if session.id == keep_session_id:
                continue
            session.revoked_at = now
            session.revoked_reason = revoked_reason
            revoked.append(session)
        await self._db.flush()
        return revoked

    async def revoke_all_for_user(
        self,
        *,
        user_id: UUID,
        revoked_reason: str,
    ) -> list[UserSession]:
        sessions = await self.list_active_for_user(user_id)
        revoked: list[UserSession] = []
        now = datetime.now(UTC)
        for session in sessions:
            session.revoked_at = now
            session.revoked_reason = revoked_reason
            revoked.append(session)
        await self._db.flush()
        return revoked

    async def revoke_all_for_user_and_tenant(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
        revoked_reason: str,
    ) -> list[UserSession]:
        sessions = await self.list_active_for_user_and_tenant(
            user_id=user_id,
            tenant_id=tenant_id,
        )
        revoked: list[UserSession] = []
        now = datetime.now(UTC)
        for session in sessions:
            session.revoked_at = now
            session.revoked_reason = revoked_reason
            revoked.append(session)
        await self._db.flush()
        return revoked


class InvitationRepository:
    """Data access for the Invitation model."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, invitation_id: UUID) -> Invitation | None:
        result = await self._db.execute(
            select(Invitation).where(Invitation.id == invitation_id)
        )
        return result.scalar_one_or_none()

    async def get_by_token_hash(self, token_hash: str) -> Invitation | None:
        result = await self._db.execute(
            select(Invitation).where(Invitation.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def get_pending_by_email_and_tenant(
        self, email: str, tenant_id: UUID
    ) -> list[Invitation]:
        result = await self._db.execute(
            select(Invitation).where(
                Invitation.email == email.lower().strip(),
                Invitation.tenant_id == tenant_id,
                Invitation.status == "pending",
            )
        )
        return list(result.scalars().all())

    async def get_by_tenant(self, tenant_id: UUID) -> list[Invitation]:
        result = await self._db.execute(
            select(Invitation)
            .where(Invitation.tenant_id == tenant_id)
            .order_by(Invitation.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        tenant_id: UUID,
        email: str,
        role_code: str,
        invited_by_user_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> Invitation:
        invitation = Invitation(
            tenant_id=tenant_id,
            email=email.lower().strip(),
            role_code=role_code,
            invited_by_user_id=invited_by_user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self._db.add(invitation)
        await self._db.flush()
        await self._db.refresh(invitation)
        return invitation

    async def mark_accepted(
        self, invitation_id: UUID, accepted_by_user_id: UUID
    ) -> None:
        await self._db.execute(
            update(Invitation)
            .where(Invitation.id == invitation_id)
            .values(
                status="accepted",
                accepted_at=datetime.now(UTC),
                accepted_by_user_id=accepted_by_user_id,
                updated_at=datetime.now(UTC),
            )
        )

    async def mark_cancelled(self, invitation_id: UUID) -> None:
        await self._db.execute(
            update(Invitation)
            .where(Invitation.id == invitation_id)
            .values(
                status="cancelled",
                updated_at=datetime.now(UTC),
            )
        )


class PasswordResetRepository:
    """Data access for the PasswordResetToken model."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_token_hash(self, token_hash: str) -> PasswordResetToken | None:
        result = await self._db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash
            )
        )
        return result.scalar_one_or_none()

    async def get_valid_by_user_id(self, user_id: UUID) -> list[PasswordResetToken]:
        now = datetime.now(UTC)
        result = await self._db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.expires_at > now,
                PasswordResetToken.used_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def create(
        self, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> PasswordResetToken:
        prt = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self._db.add(prt)
        await self._db.flush()
        await self._db.refresh(prt)
        return prt

    async def mark_used(self, token_id: UUID) -> None:
        await self._db.execute(
            update(PasswordResetToken)
            .where(PasswordResetToken.id == token_id)
            .values(used_at=datetime.now(UTC))
        )

    async def invalidate_all_for_user(self, user_id: UUID) -> None:
        now = datetime.now(UTC)
        await self._db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used_at.is_(None),
            )
            .values(used_at=now)
        )
