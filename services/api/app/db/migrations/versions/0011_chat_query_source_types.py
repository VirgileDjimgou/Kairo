"""add chat query source types

Revision ID: 0011_chat_query_source_types
Revises: 0010_document_version_fk
Create Date: 2026-07-02
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0011_chat_query_source_types"
down_revision = "0010_document_version_fk"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chat_query_logs",
        sa.Column("source_types_json", sa.Text(), nullable=False, server_default=sa.text("'[]'")),
    )


def downgrade() -> None:
    op.drop_column("chat_query_logs", "source_types_json")
