"""add missing FK constraint on documents.current_version_id

Revision ID: 0010_document_version_fk
Revises: 0009_user_sessions
Create Date: 2026-06-29
"""

from alembic import op

revision = "0010_document_version_fk"
down_revision = "0009_user_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_foreign_key(
        "fk_documents_current_version",
        "documents",
        "document_versions",
        ["current_version_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_documents_current_version",
        "documents",
        type_="foreignkey",
    )
