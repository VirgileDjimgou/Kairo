"""add internal domain event outbox and audit projection deduplication

Revision ID: 0030
Revises: 0029
"""

import sqlalchemy as sa
from alembic import op

revision = "0030"
down_revision = "0029"
branch_labels = None
depends_on = None

_UUID = sa.UUID(as_uuid=True)

_DOMAIN_EVENT_INDEXES = (
    "tenant_id",
    "actor_user_id",
    "event_type",
    "aggregate_id",
    "correlation_id",
    "status",
    "available_at",
)


def upgrade() -> None:
    op.create_table(
        "domain_events",
        sa.Column("id", _UUID, nullable=False),
        sa.Column(
            "tenant_id",
            _UUID,
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "actor_user_id",
            _UUID,
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("event_type", sa.String(120), nullable=False),
        sa.Column("aggregate_type", sa.String(120), nullable=False),
        sa.Column("aggregate_id", sa.String(120), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("correlation_id", sa.String(120), nullable=True),
        sa.Column("deduplication_key", sa.String(255), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "applied_handlers_json",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "deduplication_key", name="uq_domain_events_dedup"),
    )
    for column in _DOMAIN_EVENT_INDEXES:
        op.create_index(f"ix_domain_events_{column}", "domain_events", [column])

    op.add_column(
        "audit_events",
        sa.Column("deduplication_key", sa.String(255), nullable=True),
    )
    op.create_unique_constraint(
        "uq_audit_events_dedup", "audit_events", ["tenant_id", "deduplication_key"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_audit_events_dedup", "audit_events", type_="unique")
    op.drop_column("audit_events", "deduplication_key")
    for column in reversed(_DOMAIN_EVENT_INDEXES):
        op.drop_index(f"ix_domain_events_{column}", table_name="domain_events")
    op.drop_table("domain_events")
