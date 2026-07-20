"""Create catalog, leads, conversations and fallback tables."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260620_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "subdivisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("introduction", sa.Text(), nullable=False),
        sa.Column("location", sa.Text(), nullable=False),
        sa.Column("handover_status", sa.String(100), nullable=False),
        sa.Column("thumbnail_url", sa.String(500)),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamps(),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_subdivisions_slug", "subdivisions", ["slug"])
    op.create_index("ix_subdivisions_is_published", "subdivisions", ["is_published"])

    op.create_table(
        "apartment_specs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subdivision_id", sa.Integer(), sa.ForeignKey("subdivisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("unit_type", sa.String(50), nullable=False),
        sa.Column("area_min", sa.Numeric(8, 2)),
        sa.Column("area_max", sa.Numeric(8, 2)),
        sa.Column("area_note", sa.String(100)),
        sa.Column("price_min", sa.Numeric(14, 2)),
        sa.Column("price_max", sa.Numeric(14, 2)),
        sa.Column("price_note", sa.String(150)),
        sa.Column("currency", sa.String(10), nullable=False, server_default="VND"),
        sa.UniqueConstraint("subdivision_id", "unit_type"),
    )
    op.create_index("ix_apartment_specs_subdivision_id", "apartment_specs", ["subdivision_id"])

    op.create_table(
        "amenities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subdivision_id", sa.Integer(), sa.ForeignKey("subdivisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("scope", sa.String(20), nullable=False),
        sa.Column("description", sa.Text()),
    )
    op.create_index("ix_amenities_subdivision_id", "amenities", ["subdivision_id"])
    op.create_index("ix_amenities_scope", "amenities", ["scope"])

    op.create_table(
        "sales_policies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subdivision_id", sa.Integer(), sa.ForeignKey("subdivisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("policy_content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="published"),
        *_timestamps(),
    )
    op.create_index("ix_sales_policies_subdivision_id", "sales_policies", ["subdivision_id"])
    op.create_index("ix_sales_policies_status", "sales_policies", ["status"])

    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255)),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("budget_min", sa.Numeric(14, 2)),
        sa.Column("budget_max", sa.Numeric(14, 2)),
        sa.Column("preferred_bedrooms", sa.String(50)),
        sa.Column("customer_type", sa.String(50), nullable=False, server_default="Khác"),
        sa.Column("status", sa.String(30), nullable=False, server_default="new"),
        sa.Column("source", sa.String(30), nullable=False, server_default="contact_form"),
        sa.Column("summary", sa.Text()),
        *_timestamps(),
    )
    op.create_index("ix_leads_phone", "leads", ["phone"])
    op.create_index("ix_leads_status", "leads", ["status"])
    op.create_index("ix_leads_customer_type", "leads", ["customer_type"])

    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.String(100), nullable=False, unique=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id", ondelete="SET NULL")),
        sa.Column("subdivision_id", sa.Integer(), sa.ForeignKey("subdivisions.id", ondelete="SET NULL")),
        sa.Column("status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_message_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_conversations_session_id", "conversations", ["session_id"])
    op.create_index("ix_conversations_lead_id", "conversations", ["lead_id"])
    op.create_index("ix_conversations_status", "conversations", ["status"])

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_messages_conversation_created", "messages", ["conversation_id", "created_at"])

    op.create_table(
        "fallback_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("keyword", sa.String(255), nullable=False, unique=True),
        sa.Column("response_message", sa.Text(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamps(),
    )
    op.create_index("ix_fallback_rules_is_active", "fallback_rules", ["is_active"])


def downgrade() -> None:
    for table in (
        "fallback_rules",
        "messages",
        "conversations",
        "leads",
        "sales_policies",
        "amenities",
        "apartment_specs",
        "subdivisions",
    ):
        op.drop_table(table)
