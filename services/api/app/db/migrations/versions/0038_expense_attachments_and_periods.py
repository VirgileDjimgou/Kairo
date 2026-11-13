"""add expense attachments and finance period closing

Revision ID: 0038
Revises: 0037
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0038"
down_revision = "0037"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "expense_records",
        sa.Column("attachment_bucket", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "expense_records",
        sa.Column("attachment_key", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "expense_records",
        sa.Column("attachment_file_name", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "expense_records",
        sa.Column("attachment_content_type", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "expense_records",
        sa.Column("attachment_size_bytes", sa.Integer(), nullable=True),
    )
    op.add_column(
        "expense_records",
        sa.Column("attachment_uploaded_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "expense_records",
        sa.Column("attachment_uploaded_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_expense_records_attachment_uploaded_by_users",
        "expense_records",
        "users",
        ["attachment_uploaded_by"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "finance_periods",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "closed_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("reopened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "reopened_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("reopen_reason", sa.Text(), nullable=True),
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
        sa.UniqueConstraint("tenant_id", "year", name="uq_finance_periods_tenant_year"),
    )
    op.create_index("ix_finance_periods_tenant_id", "finance_periods", ["tenant_id"])
    op.create_index("ix_finance_periods_year", "finance_periods", ["year"])


def downgrade() -> None:
    op.drop_index("ix_finance_periods_year", table_name="finance_periods")
    op.drop_index("ix_finance_periods_tenant_id", table_name="finance_periods")
    op.drop_table("finance_periods")
    op.drop_constraint(
        "fk_expense_records_attachment_uploaded_by_users",
        "expense_records",
        type_="foreignkey",
    )
    op.drop_column("expense_records", "attachment_uploaded_by")
    op.drop_column("expense_records", "attachment_uploaded_at")
    op.drop_column("expense_records", "attachment_size_bytes")
    op.drop_column("expense_records", "attachment_content_type")
    op.drop_column("expense_records", "attachment_file_name")
    op.drop_column("expense_records", "attachment_key")
    op.drop_column("expense_records", "attachment_bucket")
