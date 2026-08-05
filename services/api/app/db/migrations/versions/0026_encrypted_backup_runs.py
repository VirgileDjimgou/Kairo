"""add encrypted backup run registry

Revision ID: 0026
Revises: 0025
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0026"
down_revision = "0025"
branch_labels = None
depends_on = None


def _uuid_type():
    return sa.String(length=36).with_variant(postgresql.UUID(as_uuid=True), "postgresql")


def upgrade() -> None:
    op.create_table(
        "backup_runs",
        sa.Column("id", _uuid_type(), nullable=False),
        sa.Column("tenant_id", _uuid_type(), nullable=False),
        sa.Column("requested_by", _uuid_type(), nullable=True),
        sa.Column("trigger", sa.String(length=32), nullable=False, server_default="manual"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("storage_reference", sa.String(length=512), nullable=True),
        sa.Column("archive_sha256", sa.String(length=64), nullable=True),
        sa.Column("manifest_sha256", sa.String(length=64), nullable=True),
        sa.Column("archive_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("components_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("error_code", sa.String(length=120), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_backup_runs_tenant_id", "backup_runs", ["tenant_id"])
    op.create_index("ix_backup_runs_requested_by", "backup_runs", ["requested_by"])
    op.create_index("ix_backup_runs_status", "backup_runs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_backup_runs_status", table_name="backup_runs")
    op.drop_index("ix_backup_runs_requested_by", table_name="backup_runs")
    op.drop_index("ix_backup_runs_tenant_id", table_name="backup_runs")
    op.drop_table("backup_runs")
