from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.models import Invitation, PasswordResetToken, User


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
                last_login_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )

    async def update_password(self, user_id: UUID, new_password_hash: str) -> None:
        await self._db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                password_hash=new_password_hash,
                updated_at=datetime.now(timezone.utc),
            )
        )

    async def set_totp_secret(self, user_id: UUID, secret: str) -> None:
        await self._db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                totp_secret=secret,
                updated_at=datetime.now(timezone.utc),
            )
        )

    async def enable_totp(self, user_id: UUID) -> None:
        await self._db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                totp_enabled=True,
                updated_at=datetime.now(timezone.utc),
            )
        )

    async def disable_totp(self, user_id: UUID) -> None:
        await self._db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                totp_secret=None,
                totp_enabled=False,
                updated_at=datetime.now(timezone.utc),
            )
        )


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
                accepted_at=datetime.now(timezone.utc),
                accepted_by_user_id=accepted_by_user_id,
                updated_at=datetime.now(timezone.utc),
            )
        )

    async def mark_cancelled(self, invitation_id: UUID) -> None:
        await self._db.execute(
            update(Invitation)
            .where(Invitation.id == invitation_id)
            .values(
                status="cancelled",
                updated_at=datetime.now(timezone.utc),
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
        now = datetime.now(timezone.utc)
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
            .values(used_at=datetime.now(timezone.utc))
        )

    async def invalidate_all_for_user(self, user_id: UUID) -> None:
        now = datetime.now(timezone.utc)
        await self._db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used_at.is_(None),
            )
            .values(used_at=now)
        )
