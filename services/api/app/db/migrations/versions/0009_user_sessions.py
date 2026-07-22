"""add user_sessions table for session governance (Sprint 32)

Revision ID: 0009_user_sessions
Revises: 0008_audit_events
Create Date: 2026-06-29
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0009_user_sessions"
down_revision = "0008_audit_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "current_tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("created_ip", sa.String(length=128), nullable=True),
        sa.Column("created_user_agent", sa.Text(), nullable=True),
        sa.Column("last_seen_ip", sa.String(length=128), nullable=True),
        sa.Column("last_seen_user_agent", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=True,
            index=True,
        ),
        sa.Column("revoked_reason", sa.String(length=120), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("user_sessions")
