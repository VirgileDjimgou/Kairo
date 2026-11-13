"""add payment reversal and idempotency integrity

Revision ID: 0037
Revises: 0036

Payments become the single source of truth for a contribution balance:
- ``idempotency_key`` makes a repeated submission harmless and is unique per tenant;
- ``reversed_at`` / ``reversed_by`` / ``reversal_reason`` keep a reversal in the
  ledger instead of deleting the payment.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0037"
down_revision = "0036"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "payment_records",
        sa.Column("idempotency_key", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "payment_records",
        sa.Column("reversed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "payment_records",
        sa.Column("reversed_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "payment_records",
        sa.Column("reversal_reason", sa.Text(), nullable=True),
    )
    op.create_foreign_key(
        "fk_payment_records_reversed_by_users",
        "payment_records",
        "users",
        ["reversed_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_unique_constraint(
        "uq_payment_records_tenant_idempotency",
        "payment_records",
        ["tenant_id", "idempotency_key"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_payment_records_tenant_idempotency",
        "payment_records",
        type_="unique",
    )
    op.drop_constraint(
        "fk_payment_records_reversed_by_users",
        "payment_records",
        type_="foreignkey",
    )
    op.drop_column("payment_records", "reversal_reason")
    op.drop_column("payment_records", "reversed_by")
    op.drop_column("payment_records", "reversed_at")
    op.drop_column("payment_records", "idempotency_key")
