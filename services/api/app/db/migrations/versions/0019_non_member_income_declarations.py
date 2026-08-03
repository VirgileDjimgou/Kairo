"""support non-member income declarations

Revision ID: 0019
Revises: 0018
"""

import sqlalchemy as sa
from alembic import op


revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("contribution_receipt_declarations", "membership_profile_id", nullable=True)
    op.add_column(
        "contribution_receipt_declarations",
        sa.Column("income_type", sa.String(length=64), nullable=False, server_default="membership_contribution"),
    )
    op.add_column("contribution_receipt_declarations", sa.Column("source_name", sa.String(length=255), nullable=True))
    op.create_index("ix_contribution_receipt_declarations_income_type", "contribution_receipt_declarations", ["income_type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_contribution_receipt_declarations_income_type", table_name="contribution_receipt_declarations")
    op.drop_column("contribution_receipt_declarations", "source_name")
    op.drop_column("contribution_receipt_declarations", "income_type")
    op.alter_column("contribution_receipt_declarations", "membership_profile_id", nullable=False)
