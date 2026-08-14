"""add tenant isolated Firebase Android push tokens

Revision ID: 0028
Revises: 0027
"""

import sqlalchemy as sa
from alembic import op


revision = "0028"
down_revision = "0027"
branch_labels = None
depends_on = None


def _uuid() -> sa.UUID:
    return sa.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table(
        "firebase_push_subscriptions",
        sa.Column("id", _uuid(), nullable=False),
        sa.Column("tenant_id", _uuid(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", _uuid(), sa.ForeignKey("notification_devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fcm_token", sa.Text(), nullable=False),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", "fcm_token", name="uq_firebase_push_device_token"),
    )
    for column in ("tenant_id", "device_id", "disabled_at"):
        op.create_index(f"ix_firebase_push_subscriptions_{column}", "firebase_push_subscriptions", [column])


def downgrade() -> None:
    for column in ("disabled_at", "device_id", "tenant_id"):
        op.drop_index(f"ix_firebase_push_subscriptions_{column}", table_name="firebase_push_subscriptions")
    op.drop_table("firebase_push_subscriptions")
