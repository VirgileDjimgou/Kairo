"""add treasury handover control fields

Revision ID: 0021
Revises: 0020
"""

import sqlalchemy as sa
from alembic import op

revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    table = "contribution_receipt_declarations"
    op.add_column(table, sa.Column("handover_reminder_days", sa.Integer(), nullable=True))
    op.add_column(table, sa.Column("handover_reminder_updated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(table, sa.Column("treasury_receipt_note", sa.Text(), nullable=True))


def downgrade() -> None:
    table = "contribution_receipt_declarations"
    op.drop_column(table, "treasury_receipt_note")
    op.drop_column(table, "handover_reminder_updated_at")
    op.drop_column(table, "handover_reminder_days")
