"""add membership type to membership profiles

Revision ID: 0016
Revises: 0015
"""

import sqlalchemy as sa
from alembic import op

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "membership_profiles",
        sa.Column("membership_type", sa.String(length=32), nullable=False, server_default="individual"),
    )


def downgrade() -> None:
    op.drop_column("membership_profiles", "membership_type")
