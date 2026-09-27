"""add canonical notification envelope fields to the authenticated inbox

Revision ID: 0031
Revises: 0030
"""

import sqlalchemy as sa
from alembic import op

revision = "0031"
down_revision = "0030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_notifications",
        sa.Column("event_id", sa.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "user_notifications",
        sa.Column("correlation_id", sa.String(120), nullable=True),
    )
    op.create_index(
        "ix_user_notifications_event_id", "user_notifications", ["event_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_user_notifications_event_id", table_name="user_notifications")
    op.drop_column("user_notifications", "correlation_id")
    op.drop_column("user_notifications", "event_id")
