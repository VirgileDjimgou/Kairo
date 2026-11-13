"""add planned budget lines

Revision ID: 0041
Revises: 0040
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0041"
down_revision = "0040"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "finance_budget_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("planned_amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
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
        sa.UniqueConstraint(
            "tenant_id",
            "year",
            "direction",
            "category",
            name="uq_finance_budget_lines_tenant_year_direction_category",
        ),
    )
    op.create_index(
        "ix_finance_budget_lines_tenant_id", "finance_budget_lines", ["tenant_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_finance_budget_lines_tenant_id", table_name="finance_budget_lines")
    op.drop_table("finance_budget_lines")
