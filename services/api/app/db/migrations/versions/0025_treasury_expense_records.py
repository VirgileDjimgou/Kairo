"""add treasurer expense records

Revision ID: 0025
Revises: 0024
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0025"
down_revision = "0024"
branch_labels = None
depends_on = None


def _uuid_type():
    return sa.String(length=36).with_variant(postgresql.UUID(as_uuid=True), "postgresql")


def upgrade() -> None:
    op.create_table(
        "expense_records",
        sa.Column("id", _uuid_type(), nullable=False),
        sa.Column("tenant_id", _uuid_type(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
        sa.Column("spent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("payee", sa.String(length=255), nullable=True),
        sa.Column("payment_method", sa.String(length=50), nullable=False, server_default="other"),
        sa.Column("reference", sa.String(length=255), nullable=True),
        sa.Column("created_by", _uuid_type(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_expense_records_tenant_id", "expense_records", ["tenant_id"])
    op.create_index("ix_expense_records_category", "expense_records", ["category"])
    op.create_index("ix_expense_records_spent_at", "expense_records", ["spent_at"])


def downgrade() -> None:
    op.drop_index("ix_expense_records_spent_at", table_name="expense_records")
    op.drop_index("ix_expense_records_category", table_name="expense_records")
    op.drop_index("ix_expense_records_tenant_id", table_name="expense_records")
    op.drop_table("expense_records")
