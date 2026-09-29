"""add composite indexes for hot read paths

Revision ID: 0032
Revises: 0031
"""

from alembic import op

revision = "0032"
down_revision = "0031"
branch_labels = None
depends_on = None

_INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("ix_contribution_records_tenant_year", "contribution_records", ("tenant_id", "year")),
    (
        "ix_payment_records_tenant_paid_at",
        "payment_records",
        ("tenant_id", "paid_at"),
    ),
    (
        "ix_audit_events_tenant_created_at",
        "audit_events",
        ("tenant_id", "created_at"),
    ),
    (
        "ix_user_notifications_tenant_recipient_created",
        "user_notifications",
        ("tenant_id", "recipient_user_id", "created_at"),
    ),
    (
        "ix_notification_outbox_status_available",
        "notification_outbox_events",
        ("status", "available_at"),
    ),
    (
        "ix_domain_events_status_available",
        "domain_events",
        ("status", "available_at"),
    ),
    (
        "ix_chat_conversations_user_updated",
        "chat_conversations",
        ("user_id", "updated_at"),
    ),
    (
        "ix_receipt_declarations_handover_due",
        "contribution_receipt_declarations",
        ("tenant_id", "cash_handover_status", "handover_due_at"),
    ),
    (
        "ix_contribution_reminders_tenant_sent",
        "contribution_reminders",
        ("tenant_id", "sent_at"),
    ),
    (
        "ix_expense_records_tenant_spent_at",
        "expense_records",
        ("tenant_id", "spent_at"),
    ),
)


def upgrade() -> None:
    for name, table, columns in _INDEXES:
        op.create_index(name, table, list(columns))


def downgrade() -> None:
    for name, table, _columns in reversed(_INDEXES):
        op.drop_index(name, table_name=table)
