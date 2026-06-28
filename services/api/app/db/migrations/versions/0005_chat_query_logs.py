"""add chat query logs

Revision ID: 0005_chat_query_logs
Revises: 0004_document_allowed_role_ids
Create Date: 2026-06-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0005_chat_query_logs"
down_revision = "0004_document_allowed_role_ids"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_query_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("refused", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("refusal_reason", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("citations_json", sa.Text(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index(
        "ix_chat_query_logs_tenant_id",
        "chat_query_logs",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_chat_query_logs_user_id",
        "chat_query_logs",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_chat_query_logs_user_id", table_name="chat_query_logs")
    op.drop_index("ix_chat_query_logs_tenant_id", table_name="chat_query_logs")
    op.drop_table("chat_query_logs")
