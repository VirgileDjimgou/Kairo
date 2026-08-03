"""track validated receipts until funds reach treasury

Revision ID: 0020
Revises: 0019
"""

import sqlalchemy as sa
from alembic import op

revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    table = "contribution_receipt_declarations"
    op.add_column(table, sa.Column("disciplinary_record_id", sa.UUID(as_uuid=True), sa.ForeignKey("disciplinary_records.id", ondelete="SET NULL"), nullable=True))
    op.add_column(table, sa.Column("cash_handover_status", sa.String(length=50), nullable=True))
    op.add_column(table, sa.Column("handover_due_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(table, sa.Column("handover_reported_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(table, sa.Column("handover_reported_by_user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True))
    op.add_column(table, sa.Column("handover_method", sa.String(length=50), nullable=True))
    op.add_column(table, sa.Column("treasury_received_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(table, sa.Column("treasury_received_by_user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True))
    op.create_index("ix_contribution_receipt_declarations_cash_handover_status", table, ["cash_handover_status"], unique=False)


def downgrade() -> None:
    table = "contribution_receipt_declarations"
    op.drop_index("ix_contribution_receipt_declarations_cash_handover_status", table_name=table)
    for column in ("treasury_received_by_user_id", "treasury_received_at", "handover_method", "handover_reported_by_user_id", "handover_reported_at", "handover_due_at", "cash_handover_status", "disciplinary_record_id"):
        op.drop_column(table, column)
