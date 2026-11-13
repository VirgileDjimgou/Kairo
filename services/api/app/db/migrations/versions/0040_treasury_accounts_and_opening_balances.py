"""add treasury accounts and opening balances

Revision ID: 0040
Revises: 0039
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0040"
down_revision = "0039"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "finance_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False, server_default="cash"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("tenant_id", "name", name="uq_finance_accounts_tenant_name"),
    )
    op.create_index("ix_finance_accounts_tenant_id", "finance_accounts", ["tenant_id"])

    op.create_table(
        "finance_opening_balances",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("finance_accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "account_id",
            "year",
            name="uq_finance_opening_balances_tenant_account_year",
        ),
    )
    op.create_index(
        "ix_finance_opening_balances_tenant_id",
        "finance_opening_balances",
        ["tenant_id"],
    )
    op.create_index(
        "ix_finance_opening_balances_account_id",
        "finance_opening_balances",
        ["account_id"],
    )

    op.add_column(
        "payment_records",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_payment_records_account_id_finance_accounts",
        "payment_records",
        "finance_accounts",
        ["account_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.add_column(
        "expense_records",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_expense_records_account_id_finance_accounts",
        "expense_records",
        "finance_accounts",
        ["account_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_expense_records_account_id_finance_accounts",
        "expense_records",
        type_="foreignkey",
    )
    op.drop_column("expense_records", "account_id")
    op.drop_constraint(
        "fk_payment_records_account_id_finance_accounts",
        "payment_records",
        type_="foreignkey",
    )
    op.drop_column("payment_records", "account_id")
    op.drop_index("ix_finance_opening_balances_account_id", table_name="finance_opening_balances")
    op.drop_index("ix_finance_opening_balances_tenant_id", table_name="finance_opening_balances")
    op.drop_table("finance_opening_balances")
    op.drop_index("ix_finance_accounts_tenant_id", table_name="finance_accounts")
    op.drop_table("finance_accounts")
