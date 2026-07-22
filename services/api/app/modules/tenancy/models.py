import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import text

from app.db.base import Base

# ── Association tables (no ORM class — plain Table objects) ───────────────────

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "tenant_user_id",
        UUID(as_uuid=True),
        ForeignKey("tenant_users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)


# ── ORM models ────────────────────────────────────────────────────────────────

class Tenant(Base):
    """
    A tenant represents one organization using the platform.

    Every piece of organizational data is scoped to a tenant_id.
    The tenant itself is not scoped — it is a top-level entity.
    """

    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="association"
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="active"
    )
    default_language: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default="fr"
    )
    branding_json: Mapped[dict] = mapped_column(
        Text, nullable=False, server_default=text("'{}'")
    )
    settings_json: Mapped[dict] = mapped_column(
        Text, nullable=False, server_default=text("'{}'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    def __repr__(self) -> str:
        return f"<Tenant slug={self.slug} name={self.name}>"


class TenantUser(Base):
    """
    Junction between a User and a Tenant.

    Captures membership status, profile type (member, admin, etc.),
    and join date. Every tenant-scoped operation should verify the user
    has an active TenantUser record for the target tenant.
    """

    __tablename__ = "tenant_users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    membership_status: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="active"
    )
    profile_type: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="member"
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    def __repr__(self) -> str:
        return f"<TenantUser tenant={self.tenant_id} user={self.user_id}>"


class Role(Base):
    """
    A role within a tenant (e.g., admin, member, treasurer).

    Roles are tenant-scoped. System roles cannot be deleted.
    Role codes are used in JWT claims to avoid DB lookups on every request.
    """

    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system_role: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    def __repr__(self) -> str:
        return f"<Role tenant={self.tenant_id} code={self.code}>"


class Permission(Base):
    """
    A platform-wide permission code (e.g., documents:upload, admin:all).

    Permissions are global (not tenant-scoped) and assigned to roles.
    """

    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Permission code={self.code}>"


# Type aliases — referenced by Table objects above (used in type checking only)
RolePermission = role_permissions
UserRole = user_roles
