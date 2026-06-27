"""Initial identity and tenancy tables.

Revision ID: 0001
Revises:
Create Date: 2026-06-26

Creates: tenants, users, tenant_users, roles, permissions,
         role_permissions, user_roles
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── tenants ────────────────────────────────────────────────────────────────
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False, server_default="association"),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("default_language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("branding_json", sa.Text(), nullable=False, server_default="'{}'"),
        sa.Column("settings_json", sa.Text(), nullable=False, server_default="'{}'"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_unique_constraint("uq_tenants_slug", "tenants", ["slug"])
    op.create_index("ix_tenants_slug", "tenants", ["slug"])

    # ── users ──────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_index("ix_users_email", "users", ["email"])

    # ── tenant_users ───────────────────────────────────────────────────────────
    op.create_table(
        "tenant_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "membership_status", sa.String(50), nullable=False, server_default="active"
        ),
        sa.Column(
            "profile_type", sa.String(50), nullable=False, server_default="member"
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_index("ix_tenant_users_tenant_id", "tenant_users", ["tenant_id"])
    op.create_index("ix_tenant_users_user_id", "tenant_users", ["user_id"])
    op.create_unique_constraint(
        "uq_tenant_users_tenant_user", "tenant_users", ["tenant_id", "user_id"]
    )

    # ── roles ──────────────────────────────────────────────────────────────────
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_system_role", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_index("ix_roles_tenant_id", "roles", ["tenant_id"])
    op.create_unique_constraint(
        "uq_roles_tenant_code", "roles", ["tenant_id", "code"]
    )

    # ── permissions ────────────────────────────────────────────────────────────
    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_unique_constraint("uq_permissions_code", "permissions", ["code"])

    # ── role_permissions ───────────────────────────────────────────────────────
    op.create_table(
        "role_permissions",
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "permission_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("permissions.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
    )

    # ── user_roles ─────────────────────────────────────────────────────────────
    op.create_table(
        "user_roles",
        sa.Column(
            "tenant_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenant_users.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("user_roles")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_index("ix_roles_tenant_id", table_name="roles")
    op.drop_table("roles")
    op.drop_index("ix_tenant_users_tenant_id", table_name="tenant_users")
    op.drop_index("ix_tenant_users_user_id", table_name="tenant_users")
    op.drop_table("tenant_users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_tenants_slug", table_name="tenants")
    op.drop_table("tenants")
