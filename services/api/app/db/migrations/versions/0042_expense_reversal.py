"""add expense reversal

Revision ID: 0042
Revises: 0041
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0042"
down_revision = "0041"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "expense_records",
        sa.Column("reversed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "expense_records",
        sa.Column("reversed_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "expense_records",
        sa.Column("reversal_reason", sa.Text(), nullable=True),
    )
    op.create_foreign_key(
        "fk_expense_records_reversed_by_users",
        "expense_records",
        "users",
        ["reversed_by"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_expense_records_reversed_by_users",
        "expense_records",
        type_="foreignkey",
    )
    op.drop_column("expense_records", "reversal_reason")
    op.drop_column("expense_records", "reversed_by")
    op.drop_column("expense_records", "reversed_at")
