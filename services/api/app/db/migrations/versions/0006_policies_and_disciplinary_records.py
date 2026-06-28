"""add policies and disciplinary records

Revision ID: 0006_policies_and_disciplinary_records
Revises: 0005_chat_query_logs
Create Date: 2026-06-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0006_policies_and_disciplinary_records"
down_revision = "0005_chat_query_logs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "policy_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'published'")),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_policy_records_tenant_id", "policy_records", ["tenant_id"], unique=False)
    op.create_index("ix_policy_records_category", "policy_records", ["category"], unique=False)

    op.create_table(
        "disciplinary_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "membership_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("membership_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "policy_record_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("policy_records.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default=sa.text("'EUR'")),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'open'")),
        sa.Column(
            "recorded_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_disciplinary_records_tenant_id", "disciplinary_records", ["tenant_id"], unique=False)
    op.create_index("ix_disciplinary_records_membership_profile_id", "disciplinary_records", ["membership_profile_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_disciplinary_records_membership_profile_id", table_name="disciplinary_records")
    op.drop_index("ix_disciplinary_records_tenant_id", table_name="disciplinary_records")
    op.drop_table("disciplinary_records")
    op.drop_index("ix_policy_records_category", table_name="policy_records")
    op.drop_index("ix_policy_records_tenant_id", table_name="policy_records")
    op.drop_table("policy_records")
