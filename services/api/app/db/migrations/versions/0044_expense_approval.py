"""add expense approval trail

Revision ID: 0044
Revises: 0043
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0044"
down_revision = "0043"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "expense_records",
        sa.Column("status", sa.String(length=20), nullable=False, server_default="recorded"),
    )
    op.add_column(
        "expense_records",
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "expense_records",
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "expense_records",
        sa.Column("approval_note", sa.Text(), nullable=True),
    )
    op.create_foreign_key(
        "fk_expense_records_approved_by_users",
        "expense_records",
        "users",
        ["approved_by"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_expense_records_approved_by_users",
        "expense_records",
        type_="foreignkey",
    )
    op.drop_column("expense_records", "approval_note")
    op.drop_column("expense_records", "approved_by")
    op.drop_column("expense_records", "approved_at")
    op.drop_column("expense_records", "status")
