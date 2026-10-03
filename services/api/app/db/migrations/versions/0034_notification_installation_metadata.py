"""normalize browser notification installation metadata

Revision ID: 0034
Revises: 0033
"""

import sqlalchemy as sa
from alembic import op

revision = "0034"
down_revision = "0033"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("notification_devices", sa.Column("browser", sa.String(length=80), nullable=True))
    op.add_column(
        "notification_devices",
        sa.Column("device_metadata_json", sa.Text(), nullable=False, server_default="{}"),
    )
    op.add_column(
        "notification_devices",
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
    )
    op.add_column(
        "notification_devices",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.add_column("notification_devices", sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_notification_devices_status", "notification_devices", ["status"])

    op.add_column(
        "web_push_subscriptions",
        sa.Column("provider", sa.String(length=20), nullable=False, server_default="web_push"),
    )
    op.add_column(
        "firebase_push_subscriptions",
        sa.Column("provider", sa.String(length=20), nullable=False, server_default="firebase"),
    )
    op.add_column("firebase_push_subscriptions", sa.Column("platform", sa.String(length=80), nullable=True))


def downgrade() -> None:
    op.drop_column("firebase_push_subscriptions", "platform")
    op.drop_column("firebase_push_subscriptions", "provider")
    op.drop_column("web_push_subscriptions", "provider")
    op.drop_index("ix_notification_devices_status", table_name="notification_devices")
    op.drop_column("notification_devices", "revoked_at")
    op.drop_column("notification_devices", "updated_at")
    op.drop_column("notification_devices", "status")
    op.drop_column("notification_devices", "device_metadata_json")
    op.drop_column("notification_devices", "browser")
