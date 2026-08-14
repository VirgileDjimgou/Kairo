"""bind Firebase push tokens to the active authenticated profile

Revision ID: 0029
Revises: 0028
"""

import sqlalchemy as sa
from alembic import op


revision = "0029"
down_revision = "0028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "firebase_push_subscriptions",
        sa.Column("recipient_user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
    )
    # Older device-only subscriptions must opt in again before delivery.
    op.execute("UPDATE firebase_push_subscriptions SET disabled_at = CURRENT_TIMESTAMP")
    op.create_index("ix_firebase_push_subscriptions_recipient_user_id", "firebase_push_subscriptions", ["recipient_user_id"])


def downgrade() -> None:
    op.drop_index("ix_firebase_push_subscriptions_recipient_user_id", table_name="firebase_push_subscriptions")
    op.drop_column("firebase_push_subscriptions", "recipient_user_id")
