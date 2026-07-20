"""Schema V2: gộp leads + customer_accounts thành customers; thêm CRM tables.

Theo BAN_THIET_KE_V2.md:
- D1: bỏ đăng nhập khách (customer_accounts) → lead capture tên + SĐT.
- D2: một bảng `customers` duy nhất, định danh chính là phone.
- Thêm: sale_awards, user_subdivisions, permissions, user_permissions,
  customer_notes, purchase_history.
- conversations: thêm customer_id / user_message_count / is_lead_captured.
- messages: sender → role (customer→user), thêm cột meta JSON.

Data migration giữ dữ liệu: customer_accounts và leads được gộp vào
customers theo phone (lead mới nhất thắng khi trùng). Downgrade khôi phục
schema cũ và đổ customers ngược về leads (mất password_hash của
customer_accounts — không thể khôi phục, chấp nhận trong downgrade).
"""

import sqlalchemy as sa
from alembic import op

revision: str = "20260708_04"
down_revision: str | None = "20260627_03"
branch_labels = None
depends_on = None


OLD_STATUS_TO_V2 = {
    "new": "new",
    "contacted": "contacted",
    "qualified": "consulting",
    "closed": "won",
}

OLD_SOURCE_TO_V2 = {
    "contact_form": "contact_form",
    "chat": "chat",
    "chat_guest": "chat",
    "customer_register": "chat",
}


def _map_status(value: str | None) -> str:
    return OLD_STATUS_TO_V2.get((value or "").lower(), "new")


def _map_source(value: str | None) -> str:
    return OLD_SOURCE_TO_V2.get((value or "").lower(), "manual")


def upgrade() -> None:
    bind = op.get_bind()

    # ── 0. subdivisions: nới handover_status (data cleaned dài hơn 100 ký tự) ─
    with op.batch_alter_table("subdivisions") as batch:
        batch.alter_column(
            "handover_status", existing_type=sa.String(100), type_=sa.String(255), existing_nullable=False
        )

    # ── 1. users: thông tin sale mở rộng ────────────────────────────────────
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("phone", sa.String(20), nullable=True))
        batch.add_column(sa.Column("avatar_url", sa.String(500), nullable=True))
        batch.add_column(sa.Column("title", sa.String(100), nullable=True))
        batch.add_column(sa.Column("work_shift_start", sa.Time(), nullable=True))
        batch.add_column(sa.Column("work_shift_end", sa.Time(), nullable=True))
        batch.add_column(sa.Column("join_date", sa.Date(), nullable=True))

    # ── 2. Bảng mới: permissions / sale_awards / n-n ────────────────────────
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("group_name", sa.String(100), nullable=False),
    )
    op.create_index("ix_permissions_code", "permissions", ["code"], unique=True)

    op.create_table(
        "sale_awards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("award_name", sa.String(255), nullable=False),
        sa.Column("awarded_at", sa.Date(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
    )
    op.create_index("ix_sale_awards_user_id", "sale_awards", ["user_id"])

    op.create_table(
        "user_subdivisions",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column(
            "subdivision_id", sa.Integer(), sa.ForeignKey("subdivisions.id", ondelete="CASCADE"), primary_key=True
        ),
    )

    op.create_table(
        "user_permissions",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column(
            "permission_id", sa.Integer(), sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
        ),
    )

    # ── 3. customers + bảng con ─────────────────────────────────────────────
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("customer_type", sa.String(20), nullable=False, server_default="unknown"),
        sa.Column("temperature", sa.String(10), nullable=False, server_default="unknown"),
        sa.Column("lead_score", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="new"),
        sa.Column(
            "interested_subdivision_id",
            sa.Integer(),
            sa.ForeignKey("subdivisions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("preferred_unit_type", sa.String(50), nullable=True),
        sa.Column("budget_min", sa.BigInteger(), nullable=True),
        sa.Column("budget_max", sa.BigInteger(), nullable=True),
        sa.Column("purpose", sa.String(20), nullable=False, server_default="unknown"),
        sa.Column("needs_summary", sa.Text(), nullable=True),
        sa.Column("assigned_sale_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source", sa.String(30), nullable=False, server_default="chat"),
        sa.Column("consent_contact", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_contact_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_customers_phone", "customers", ["phone"], unique=True)
    op.create_index("ix_customers_customer_type", "customers", ["customer_type"])
    op.create_index("ix_customers_temperature", "customers", ["temperature"])
    op.create_index("ix_customers_status", "customers", ["status"])
    op.create_index("ix_customers_assigned_sale_id", "customers", ["assigned_sale_id"])
    op.create_index("ix_customers_interested_subdivision_id", "customers", ["interested_subdivision_id"])

    op.create_table(
        "customer_notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_customer_notes_customer_id", "customer_notes", ["customer_id"])
    op.create_index("ix_customer_notes_author_id", "customer_notes", ["author_id"])

    op.create_table(
        "purchase_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "subdivision_id", sa.Integer(), sa.ForeignKey("subdivisions.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("unit_type", sa.String(50), nullable=False),
        sa.Column("purchase_date", sa.Date(), nullable=False),
        sa.Column("price", sa.BigInteger(), nullable=False),
        sa.Column(
            "responsible_sale_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="deposit"),
        sa.Column("note", sa.Text(), nullable=True),
    )
    op.create_index("ix_purchase_history_customer_id", "purchase_history", ["customer_id"])
    op.create_index("ix_purchase_history_subdivision_id", "purchase_history", ["subdivision_id"])
    op.create_index("ix_purchase_history_responsible_sale_id", "purchase_history", ["responsible_sale_id"])

    # ── 4. Data migration: gộp customer_accounts + leads → customers ────────
    phone_to_customer: dict[str, int] = {}

    account_rows = bind.execute(
        sa.text("SELECT id, full_name, phone, created_at FROM customer_accounts ORDER BY id")
    ).mappings().all()
    account_id_to_phone = {row["id"]: row["phone"] for row in account_rows}
    for row in account_rows:
        result = bind.execute(
            sa.text(
                "INSERT INTO customers (full_name, phone, source, consent_contact, created_at, updated_at) "
                "VALUES (:full_name, :phone, 'chat', :consent, :created_at, :created_at) RETURNING id"
            ),
            {
                "full_name": row["full_name"],
                "phone": row["phone"],
                "consent": True,
                "created_at": row["created_at"],
            },
        )
        # RETURNING id chạy trên cả PostgreSQL và SQLite (>=3.35); psycopg cursor
        # không có .lastrowid nên không dùng được cách cũ.
        customer_id = result.scalar()
        phone_to_customer[row["phone"]] = customer_id

    # Lead mới nhất cho mỗi phone thắng khi trùng dữ liệu.
    lead_rows = bind.execute(
        sa.text(
            "SELECT id, name, phone, email, budget_min, budget_max, preferred_bedrooms, "
            "status, source, summary, assigned_to_id, created_at FROM leads ORDER BY id"
        )
    ).mappings().all()
    lead_id_to_phone = {row["id"]: row["phone"] for row in lead_rows}
    for row in lead_rows:
        phone = row["phone"]
        params = {
            "full_name": row["name"],
            "phone": phone,
            "email": row["email"],
            "budget_min": int(row["budget_min"]) if row["budget_min"] is not None else None,
            "budget_max": int(row["budget_max"]) if row["budget_max"] is not None else None,
            "preferred_unit_type": row["preferred_bedrooms"],
            "status": _map_status(row["status"]),
            "source": _map_source(row["source"]),
            "needs_summary": row["summary"],
            "assigned_sale_id": row["assigned_to_id"],
            "created_at": row["created_at"],
        }
        if phone in phone_to_customer:
            params["customer_id"] = phone_to_customer[phone]
            bind.execute(
                sa.text(
                    "UPDATE customers SET "
                    "full_name = COALESCE(:full_name, full_name), "
                    "email = COALESCE(:email, email), "
                    "budget_min = COALESCE(:budget_min, budget_min), "
                    "budget_max = COALESCE(:budget_max, budget_max), "
                    "preferred_unit_type = COALESCE(:preferred_unit_type, preferred_unit_type), "
                    "status = :status, source = :source, "
                    "needs_summary = COALESCE(:needs_summary, needs_summary), "
                    "assigned_sale_id = COALESCE(:assigned_sale_id, assigned_sale_id) "
                    "WHERE id = :customer_id"
                ),
                params,
            )
        else:
            result = bind.execute(
                sa.text(
                    "INSERT INTO customers (full_name, phone, email, budget_min, budget_max, "
                    "preferred_unit_type, status, source, needs_summary, assigned_sale_id, "
                    "consent_contact, created_at, updated_at) "
                    "VALUES (:full_name, :phone, :email, :budget_min, :budget_max, "
                    ":preferred_unit_type, :status, :source, :needs_summary, :assigned_sale_id, "
                    ":consent, :created_at, :created_at) RETURNING id"
                ),
                {**params, "consent": False},
            )
            customer_id = result.scalar()
            phone_to_customer[phone] = customer_id

    # customer_notes từ lead_notes (theo phone của lead).
    note_rows = bind.execute(
        sa.text("SELECT lead_id, author_id, content, created_at FROM lead_notes ORDER BY id")
    ).mappings().all()
    for row in note_rows:
        phone = lead_id_to_phone.get(row["lead_id"])
        customer_id = phone_to_customer.get(phone)
        if customer_id is None:
            continue
        bind.execute(
            sa.text(
                "INSERT INTO customer_notes (customer_id, author_id, content, created_at) "
                "VALUES (:customer_id, :author_id, :content, :created_at)"
            ),
            {
                "customer_id": customer_id,
                "author_id": row["author_id"],
                "content": row["content"],
                "created_at": row["created_at"],
            },
        )

    # ── 5. conversations: gắn customer_id, đếm tin khách ────────────────────
    with op.batch_alter_table("conversations") as batch:
        batch.add_column(sa.Column("customer_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("user_message_count", sa.Integer(), nullable=False, server_default="0"))
        batch.add_column(
            sa.Column("is_lead_captured", sa.Boolean(), nullable=False, server_default=sa.false())
        )

    conversation_rows = bind.execute(
        sa.text("SELECT id, lead_id, customer_account_id FROM conversations ORDER BY id")
    ).mappings().all()
    for row in conversation_rows:
        phone = lead_id_to_phone.get(row["lead_id"]) or account_id_to_phone.get(row["customer_account_id"])
        customer_id = phone_to_customer.get(phone)
        count = bind.execute(
            sa.text(
                "SELECT COUNT(*) FROM messages WHERE conversation_id = :cid AND sender IN ('customer', 'user')"
            ),
            {"cid": row["id"]},
        ).scalar()
        bind.execute(
            sa.text(
                "UPDATE conversations SET customer_id = :customer_id, "
                "user_message_count = :count, is_lead_captured = :captured WHERE id = :cid"
            ),
            {
                "customer_id": customer_id,
                "count": count or 0,
                "captured": customer_id is not None,
                "cid": row["id"],
            },
        )

    # Index cũ phải xoá trước khi drop cột, vì batch mode SQLite recreate bảng
    # và cố tạo lại mọi index đang tồn tại.
    op.drop_index("ix_conversations_lead_id", table_name="conversations")
    op.drop_index("ix_conversations_status", table_name="conversations")
    op.drop_index("ix_conversations_customer_account_id", table_name="conversations")
    with op.batch_alter_table("conversations") as batch:
        batch.create_foreign_key(
            "fk_conversations_customer_id_customers", "customers", ["customer_id"], ["id"], ondelete="SET NULL"
        )
        batch.drop_column("lead_id")
        batch.drop_column("customer_account_id")
        batch.drop_column("status")
    op.create_index("ix_conversations_customer_id", "conversations", ["customer_id"])

    # ── 6. messages: sender → role, thêm meta JSON ──────────────────────────
    with op.batch_alter_table("messages") as batch:
        batch.add_column(sa.Column("role", sa.String(20), nullable=False, server_default="user"))
        batch.add_column(sa.Column("meta", sa.JSON(), nullable=True))

    bind.execute(
        sa.text(
            "UPDATE messages SET role = CASE "
            "WHEN sender IN ('customer', 'user') THEN 'user' "
            "WHEN sender IN ('ai', 'assistant') THEN 'ai' "
            "ELSE 'system' END"
        )
    )

    with op.batch_alter_table("messages") as batch:
        batch.drop_column("sender")

    # ── 7. Xoá bảng legacy ───────────────────────────────────────────────────
    op.drop_table("lead_notes")
    op.drop_table("leads")
    op.drop_table("customer_accounts")


def downgrade() -> None:
    bind = op.get_bind()

    # Khôi phục bảng legacy (dữ liệu đổ ngược best-effort từ customers).
    op.create_table(
        "customer_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("password_hash", sa.String(500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("chat_limit", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_customer_accounts_phone", "customer_accounts", ["phone"], unique=True)
    op.create_index("ix_customer_accounts_is_active", "customer_accounts", ["is_active"])

    # Tên FK/index phải khớp chính xác những gì migration 02/03 kỳ vọng khi
    # downgrade tiếp xuống dưới.
    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("budget_min", sa.Numeric(14, 2), nullable=True),
        sa.Column("budget_max", sa.Numeric(14, 2), nullable=True),
        sa.Column("preferred_bedrooms", sa.String(50), nullable=True),
        sa.Column("customer_type", sa.String(50), nullable=False, server_default="Khác"),
        sa.Column("status", sa.String(30), nullable=False, server_default="new"),
        sa.Column("source", sa.String(30), nullable=False, server_default="contact_form"),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("assigned_to_id", sa.Integer(), nullable=True),
        sa.Column("customer_account_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["assigned_to_id"], ["users.id"], name="fk_leads_assigned_to_id_users", ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["customer_account_id"],
            ["customer_accounts.id"],
            name="fk_leads_customer_account_id_customer_accounts",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_leads_phone", "leads", ["phone"])
    op.create_index("ix_leads_status", "leads", ["status"])
    op.create_index("ix_leads_customer_type", "leads", ["customer_type"])
    op.create_index("ix_leads_assigned_to_id", "leads", ["assigned_to_id"])
    op.create_index("ix_leads_customer_account_id", "leads", ["customer_account_id"])

    op.create_table(
        "lead_notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_lead_notes_lead_id", "lead_notes", ["lead_id"])
    op.create_index("ix_lead_notes_author_id", "lead_notes", ["author_id"])

    customer_rows = bind.execute(
        sa.text(
            "SELECT id, full_name, phone, email, budget_min, budget_max, preferred_unit_type, "
            "status, source, needs_summary, assigned_sale_id, created_at FROM customers ORDER BY id"
        )
    ).mappings().all()
    customer_to_lead: dict[int, int] = {}
    for row in customer_rows:
        result = bind.execute(
            sa.text(
                "INSERT INTO leads (name, phone, email, budget_min, budget_max, preferred_bedrooms, "
                "status, source, summary, assigned_to_id, created_at, updated_at) "
                "VALUES (:name, :phone, :email, :budget_min, :budget_max, :preferred, "
                ":status, :source, :summary, :assigned, :created_at, :created_at) RETURNING id"
            ),
            {
                "name": row["full_name"],
                "phone": row["phone"],
                "email": row["email"],
                "budget_min": row["budget_min"],
                "budget_max": row["budget_max"],
                "preferred": row["preferred_unit_type"],
                "status": row["status"] if row["status"] in ("new", "contacted") else "qualified",
                "source": row["source"] if row["source"] in ("contact_form", "chat") else "contact_form",
                "summary": row["needs_summary"],
                "assigned": row["assigned_sale_id"],
                "created_at": row["created_at"],
            },
        )
        lead_id = result.scalar()
        customer_to_lead[row["id"]] = lead_id

    note_rows = bind.execute(
        sa.text("SELECT customer_id, author_id, content, created_at FROM customer_notes ORDER BY id")
    ).mappings().all()
    for row in note_rows:
        lead_id = customer_to_lead.get(row["customer_id"])
        if lead_id is None:
            continue
        bind.execute(
            sa.text(
                "INSERT INTO lead_notes (lead_id, author_id, content, created_at) "
                "VALUES (:lead_id, :author_id, :content, :created_at)"
            ),
            {
                "lead_id": lead_id,
                "author_id": row["author_id"],
                "content": row["content"],
                "created_at": row["created_at"],
            },
        )

    # messages: role → sender
    with op.batch_alter_table("messages") as batch:
        batch.add_column(sa.Column("sender", sa.String(20), nullable=False, server_default="customer"))
    bind.execute(
        sa.text(
            "UPDATE messages SET sender = CASE "
            "WHEN role = 'user' THEN 'customer' WHEN role = 'ai' THEN 'ai' ELSE 'system' END"
        )
    )
    with op.batch_alter_table("messages") as batch:
        batch.drop_column("role")
        batch.drop_column("meta")

    # conversations: khôi phục lead_id / customer_account_id / status
    with op.batch_alter_table("conversations") as batch:
        batch.add_column(sa.Column("lead_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("customer_account_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("status", sa.String(30), nullable=False, server_default="active"))

    conversation_rows = bind.execute(
        sa.text("SELECT id, customer_id FROM conversations ORDER BY id")
    ).mappings().all()
    for row in conversation_rows:
        lead_id = customer_to_lead.get(row["customer_id"])
        if lead_id is not None:
            bind.execute(
                sa.text("UPDATE conversations SET lead_id = :lead_id WHERE id = :cid"),
                {"lead_id": lead_id, "cid": row["id"]},
            )

    op.drop_index("ix_conversations_customer_id", table_name="conversations")
    with op.batch_alter_table("conversations") as batch:
        batch.drop_constraint("fk_conversations_customer_id_customers", type_="foreignkey")
        batch.create_foreign_key("fk_conversations_lead_id_leads", "leads", ["lead_id"], ["id"], ondelete="SET NULL")
        batch.create_foreign_key(
            "fk_conversations_customer_account_id_customer_accounts",
            "customer_accounts",
            ["customer_account_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch.drop_column("customer_id")
        batch.drop_column("user_message_count")
        batch.drop_column("is_lead_captured")
    op.create_index("ix_conversations_lead_id", "conversations", ["lead_id"])
    op.create_index("ix_conversations_status", "conversations", ["status"])
    op.create_index("ix_conversations_customer_account_id", "conversations", ["customer_account_id"])

    # Xoá bảng V2
    op.drop_table("purchase_history")
    op.drop_table("customer_notes")
    op.drop_index("ix_customers_interested_subdivision_id", table_name="customers")
    op.drop_index("ix_customers_assigned_sale_id", table_name="customers")
    op.drop_index("ix_customers_status", table_name="customers")
    op.drop_index("ix_customers_temperature", table_name="customers")
    op.drop_index("ix_customers_customer_type", table_name="customers")
    op.drop_index("ix_customers_phone", table_name="customers")
    op.drop_table("customers")
    op.drop_table("user_permissions")
    op.drop_table("user_subdivisions")
    op.drop_index("ix_sale_awards_user_id", table_name="sale_awards")
    op.drop_table("sale_awards")
    op.drop_index("ix_permissions_code", table_name="permissions")
    op.drop_table("permissions")

    with op.batch_alter_table("users") as batch:
        batch.drop_column("join_date")
        batch.drop_column("work_shift_end")
        batch.drop_column("work_shift_start")
        batch.drop_column("title")
        batch.drop_column("avatar_url")
        batch.drop_column("phone")

    with op.batch_alter_table("subdivisions") as batch:
        batch.alter_column(
            "handover_status", existing_type=sa.String(255), type_=sa.String(100), existing_nullable=False
        )
