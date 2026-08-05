"""add authenticated notification inbox, device profiles and transactional outbox

Revision ID: 0023
Revises: 0022
"""

import sqlalchemy as sa
from alembic import op

revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def _uuid() -> sa.UUID:
    return sa.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table(
        "user_notifications",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("tenant_id", _uuid(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipient_user_id", _uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="normal"),
        sa.Column("target_path", sa.String(length=255), nullable=False, server_default="/dashboard"),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("deduplication_key", sa.String(length=255), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("tenant_id", "deduplication_key", name="uq_user_notifications_dedup"),
    )
    op.create_index("ix_user_notifications_tenant_id", "user_notifications", ["tenant_id"])
    op.create_index("ix_user_notifications_recipient_user_id", "user_notifications", ["recipient_user_id"])
    op.create_index("ix_user_notifications_read_at", "user_notifications", ["read_at"])
    op.create_index("ix_user_notifications_created_at", "user_notifications", ["created_at"])
    op.create_table(
        "notification_outbox_events",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("tenant_id", _uuid(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("deduplication_key", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("tenant_id", "deduplication_key", name="uq_notification_outbox_dedup"),
    )
    for column in ("tenant_id", "event_type", "status", "available_at"):
        op.create_index(f"ix_notification_outbox_events_{column}", "notification_outbox_events", [column])
    op.create_table(
        "notification_devices",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("tenant_id", _uuid(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("installation_id", sa.String(length=128), nullable=False),
        sa.Column("platform", sa.String(length=80), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("tenant_id", "installation_id", name="uq_notification_devices_installation"),
    )
    op.create_index("ix_notification_devices_tenant_id", "notification_devices", ["tenant_id"])
    op.create_table(
        "notification_device_profiles",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("tenant_id", _uuid(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", _uuid(), sa.ForeignKey("notification_devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", _uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("push_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("opted_in_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("device_id", "user_id", name="uq_notification_device_profile"),
    )
    for column in ("tenant_id", "device_id", "user_id"):
        op.create_index(f"ix_notification_device_profiles_{column}", "notification_device_profiles", [column])
    op.create_table(
        "web_push_subscriptions",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("tenant_id", _uuid(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", _uuid(), sa.ForeignKey("notification_devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False),
        sa.Column("p256dh", sa.Text(), nullable=False),
        sa.Column("auth", sa.Text(), nullable=False),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("device_id", "endpoint", name="uq_web_push_device_endpoint"),
    )
    for column in ("tenant_id", "device_id", "disabled_at"):
        op.create_index(f"ix_web_push_subscriptions_{column}", "web_push_subscriptions", [column])


def downgrade() -> None:
    for table in ("web_push_subscriptions", "notification_device_profiles", "notification_devices", "notification_outbox_events", "user_notifications"):
        op.drop_table(table)
