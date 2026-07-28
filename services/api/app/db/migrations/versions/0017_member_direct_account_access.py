"""add direct member account login identifiers and initial-password state

Revision ID: 0017
Revises: 0016
"""

from alembic import op
import sqlalchemy as sa


revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("login_identifier", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(length=20), nullable=True))
    op.add_column(
        "users",
        sa.Column("password_change_required", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("ix_users_login_identifier", "users", ["login_identifier"], unique=True)
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_phone", table_name="users")
    op.drop_index("ix_users_login_identifier", table_name="users")
    op.drop_column("users", "password_change_required")
    op.drop_column("users", "phone")
    op.drop_column("users", "login_identifier")
