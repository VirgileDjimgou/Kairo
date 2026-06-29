"""add policies and disciplinary records

Revision ID: 0006_business_modules
Revises: 0005_chat_query_logs
Create Date: 2026-06-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0006_business_modules"
down_revision = "0005_chat_query_logs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "membership_profiles",
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
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("member_code", sa.String(length=50), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_membership_profiles_tenant_id", "membership_profiles", ["tenant_id"], unique=False)
    op.create_index("ix_membership_profiles_user_id", "membership_profiles", ["user_id"], unique=False)
    op.create_index("ix_membership_profiles_member_code", "membership_profiles", ["member_code"], unique=False)

    op.create_table(
        "contribution_records",
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
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("expected_amount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("paid_amount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("balance", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default=sa.text("'EUR'")),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_contribution_records_tenant_id", "contribution_records", ["tenant_id"], unique=False)
    op.create_index(
        "ix_contribution_records_membership_profile_id",
        "contribution_records",
        ["membership_profile_id"],
        unique=False,
    )

    op.create_table(
        "payment_records",
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
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default=sa.text("'EUR'")),
        sa.Column(
            "paid_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "payment_method",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'other'"),
        ),
        sa.Column("reference", sa.String(length=255), nullable=True),
        sa.Column(
            "recorded_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_payment_records_tenant_id", "payment_records", ["tenant_id"], unique=False)
    op.create_index(
        "ix_payment_records_contribution_record_id",
        "payment_records",
        ["contribution_record_id"],
        unique=False,
    )

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column(
            "visibility_scope",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'members_only'"),
        ),
        sa.Column("allowed_role_ids_json", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'published'"),
        ),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_events_tenant_id", "events", ["tenant_id"], unique=False)

    op.create_table(
        "announcements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "visibility_scope",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'members_only'"),
        ),
        sa.Column("allowed_role_ids_json", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_announcements_tenant_id", "announcements", ["tenant_id"], unique=False)

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
    op.drop_index("ix_announcements_tenant_id", table_name="announcements")
    op.drop_table("announcements")
    op.drop_index("ix_events_tenant_id", table_name="events")
    op.drop_table("events")
    op.drop_index("ix_payment_records_contribution_record_id", table_name="payment_records")
    op.drop_index("ix_payment_records_tenant_id", table_name="payment_records")
    op.drop_table("payment_records")
    op.drop_index("ix_contribution_records_membership_profile_id", table_name="contribution_records")
    op.drop_index("ix_contribution_records_tenant_id", table_name="contribution_records")
    op.drop_table("contribution_records")
    op.drop_index("ix_membership_profiles_member_code", table_name="membership_profiles")
    op.drop_index("ix_membership_profiles_user_id", table_name="membership_profiles")
    op.drop_index("ix_membership_profiles_tenant_id", table_name="membership_profiles")
    op.drop_table("membership_profiles")
    op.drop_index("ix_disciplinary_records_membership_profile_id", table_name="disciplinary_records")
    op.drop_index("ix_disciplinary_records_tenant_id", table_name="disciplinary_records")
    op.drop_table("disciplinary_records")
    op.drop_index("ix_policy_records_category", table_name="policy_records")
    op.drop_index("ix_policy_records_tenant_id", table_name="policy_records")
    op.drop_table("policy_records")
