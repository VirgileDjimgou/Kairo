"""add tenant custom domain mapping

Revision ID: 0035
Revises: 0034
"""

import sqlalchemy as sa
from alembic import op

revision = "0035"
down_revision = "0034"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("custom_domain", sa.String(length=253), nullable=True))
    op.create_index("ix_tenants_custom_domain", "tenants", ["custom_domain"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_tenants_custom_domain", table_name="tenants")
    op.drop_column("tenants", "custom_domain")
