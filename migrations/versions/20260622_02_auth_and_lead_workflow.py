"""Add users, lead assignment and notes."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260622_02"
down_revision: str | None = "20260620_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(500), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="sale"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_is_active", "users", ["is_active"])

    with op.batch_alter_table("leads") as batch:
        batch.add_column(sa.Column("assigned_to_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_leads_assigned_to_id_users", "users", ["assigned_to_id"], ["id"], ondelete="SET NULL"
        )
        batch.create_index("ix_leads_assigned_to_id", ["assigned_to_id"])

    op.create_table(
        "lead_notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_lead_notes_lead_id", "lead_notes", ["lead_id"])
    op.create_index("ix_lead_notes_author_id", "lead_notes", ["author_id"])


def downgrade() -> None:
    op.drop_table("lead_notes")
    with op.batch_alter_table("leads") as batch:
        batch.drop_index("ix_leads_assigned_to_id")
        batch.drop_constraint("fk_leads_assigned_to_id_users", type_="foreignkey")
        batch.drop_column("assigned_to_id")
    op.drop_table("users")
