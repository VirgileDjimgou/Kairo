"""add tenant expense categories

Revision ID: 0043
Revises: 0042
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0043"
down_revision = "0042"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "finance_expense_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_finance_expense_categories_tenant_code"
        ),
    )
    op.create_index(
        "ix_finance_expense_categories_tenant_id",
        "finance_expense_categories",
        ["tenant_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_expense_categories_tenant_id",
        table_name="finance_expense_categories",
    )
    op.drop_table("finance_expense_categories")
