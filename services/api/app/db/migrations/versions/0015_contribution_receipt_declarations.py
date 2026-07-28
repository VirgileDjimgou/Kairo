"""add contribution receipt declarations

Revision ID: 0015
Revises: 0014
Create Date: 2026-07-28
"""

import sqlalchemy as sa
from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contribution_receipt_declarations",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("membership_profile_id", sa.UUID(as_uuid=True), sa.ForeignKey("membership_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("declarant_user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("declarant_role_code", sa.String(64), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="EUR"),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payment_method", sa.String(50), nullable=False, server_default="cash"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("reference", sa.String(255), nullable=True),
        sa.Column("evidence_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_by_user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("processed_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("processing_note", sa.Text(), nullable=True),
        sa.Column("contribution_record_id", sa.UUID(as_uuid=True), sa.ForeignKey("contribution_records.id", ondelete="SET NULL"), nullable=True),
        sa.Column("payment_record_id", sa.UUID(as_uuid=True), sa.ForeignKey("payment_records.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    for name, columns in (
        ("ix_contribution_receipt_declarations_tenant_id", ["tenant_id"]),
        ("ix_contribution_receipt_declarations_membership_profile_id", ["membership_profile_id"]),
        ("ix_contribution_receipt_declarations_declarant_user_id", ["declarant_user_id"]),
        ("ix_contribution_receipt_declarations_status", ["status"]),
    ):
        op.create_index(name, "contribution_receipt_declarations", columns, unique=False)


def downgrade() -> None:
    op.drop_table("contribution_receipt_declarations")
