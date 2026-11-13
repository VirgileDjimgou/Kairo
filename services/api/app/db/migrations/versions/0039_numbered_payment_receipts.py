"""add numbered payment receipts

Revision ID: 0039
Revises: 0038
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0039"
down_revision = "0038"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "payment_records",
        sa.Column("receipt_number", sa.String(length=32), nullable=True),
    )
    op.create_unique_constraint(
        "uq_payment_records_tenant_receipt_number",
        "payment_records",
        ["tenant_id", "receipt_number"],
    )
    op.create_table(
        "finance_receipt_counters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("last_number", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint(
            "tenant_id", "year", name="uq_finance_receipt_counters_tenant_year"
        ),
    )
    op.create_index(
        "ix_finance_receipt_counters_tenant_id",
        "finance_receipt_counters",
        ["tenant_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_receipt_counters_tenant_id",
        table_name="finance_receipt_counters",
    )
    op.drop_table("finance_receipt_counters")
    op.drop_constraint(
        "uq_payment_records_tenant_receipt_number",
        "payment_records",
        type_="unique",
    )
    op.drop_column("payment_records", "receipt_number")
