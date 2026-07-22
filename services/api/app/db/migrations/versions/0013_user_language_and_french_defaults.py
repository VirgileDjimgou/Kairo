"""Add user language preference and switch tenant default language to French.

Revision ID: 0013
Revises: 0012_contribution_reminders
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0013"
down_revision: str | None = "0012_contribution_reminders"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("preferred_language", sa.String(length=10), nullable=True))
    op.alter_column("tenants", "default_language", existing_type=sa.String(length=10), server_default="fr")
    op.execute("UPDATE tenants SET default_language = 'fr' WHERE default_language IS NULL OR default_language = 'en'")


def downgrade() -> None:
    op.execute("UPDATE tenants SET default_language = 'en' WHERE default_language = 'fr'")
    op.alter_column("tenants", "default_language", existing_type=sa.String(length=10), server_default="en")
    op.drop_column("users", "preferred_language")
