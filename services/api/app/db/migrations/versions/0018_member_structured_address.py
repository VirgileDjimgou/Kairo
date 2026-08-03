"""add structured member address fields

Revision ID: 0018
Revises: 0017
"""

from alembic import op
import sqlalchemy as sa


revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("membership_profiles", sa.Column("street_name", sa.String(length=160), nullable=True))
    op.add_column("membership_profiles", sa.Column("house_number", sa.String(length=32), nullable=True))
    op.add_column("membership_profiles", sa.Column("postal_code", sa.String(length=16), nullable=True))
    op.add_column("membership_profiles", sa.Column("city", sa.String(length=120), nullable=True))
    op.add_column("membership_profiles", sa.Column("country_code", sa.String(length=2), nullable=True))


def downgrade() -> None:
    op.drop_column("membership_profiles", "country_code")
    op.drop_column("membership_profiles", "city")
    op.drop_column("membership_profiles", "postal_code")
    op.drop_column("membership_profiles", "house_number")
    op.drop_column("membership_profiles", "street_name")
