"""Add customer accounts and authenticated chat sessions."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260627_03"
down_revision: str | None = "20260622_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "customer_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("chat_limit", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_customer_accounts_phone", "customer_accounts", ["phone"])
    op.create_index("ix_customer_accounts_is_active", "customer_accounts", ["is_active"])

    with op.batch_alter_table("leads") as batch:
        batch.add_column(sa.Column("customer_account_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_leads_customer_account_id_customer_accounts",
            "customer_accounts",
            ["customer_account_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch.create_index("ix_leads_customer_account_id", ["customer_account_id"])

    with op.batch_alter_table("conversations") as batch:
        batch.add_column(sa.Column("customer_account_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_conversations_customer_account_id_customer_accounts",
            "customer_accounts",
            ["customer_account_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch.create_index("ix_conversations_customer_account_id", ["customer_account_id"])


def downgrade() -> None:
    with op.batch_alter_table("conversations") as batch:
        batch.drop_index("ix_conversations_customer_account_id")
        batch.drop_constraint("fk_conversations_customer_account_id_customer_accounts", type_="foreignkey")
        batch.drop_column("customer_account_id")

    with op.batch_alter_table("leads") as batch:
        batch.drop_index("ix_leads_customer_account_id")
        batch.drop_constraint("fk_leads_customer_account_id_customer_accounts", type_="foreignkey")
        batch.drop_column("customer_account_id")

    op.drop_index("ix_customer_accounts_is_active", table_name="customer_accounts")
    op.drop_index("ix_customer_accounts_phone", table_name="customer_accounts")
    op.drop_table("customer_accounts")
