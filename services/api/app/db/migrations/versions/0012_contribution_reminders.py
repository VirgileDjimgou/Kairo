"""add contribution reminders

Revision ID: 0012_contribution_reminders
Revises: 0011_chat_query_source_types
Create Date: 2026-07-03
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0012_contribution_reminders"
down_revision = "0011_chat_query_source_types"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contribution_reminders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "contribution_record_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("contribution_records.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "membership_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("membership_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("member_display_name", sa.String(length=255), nullable=False),
        sa.Column("member_code", sa.String(length=50), nullable=False),
        sa.Column("balance_snapshot", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("due_date_snapshot", sa.DateTime(timezone=True), nullable=True),
        sa.Column("channel", sa.String(length=50), nullable=False, server_default=sa.text("'email'")),
        sa.Column(
            "delivery_status",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'simulated'"),
        ),
        sa.Column("recipient", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("provider_message", sa.Text(), nullable=True),
        sa.Column(
            "reminded_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index(
        "ix_contribution_reminders_tenant_id",
        "contribution_reminders",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_contribution_reminders_contribution_record_id",
        "contribution_reminders",
        ["contribution_record_id"],
        unique=False,
    )
    op.create_index(
        "ix_contribution_reminders_membership_profile_id",
        "contribution_reminders",
        ["membership_profile_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_contribution_reminders_membership_profile_id", table_name="contribution_reminders")
    op.drop_index("ix_contribution_reminders_contribution_record_id", table_name="contribution_reminders")
    op.drop_index("ix_contribution_reminders_tenant_id", table_name="contribution_reminders")
    op.drop_table("contribution_reminders")
