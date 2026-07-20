"""ORM schema V2 — nguồn model duy nhất của hệ thống.

Thiết kế theo BAN_THIET_KE_V2.md Mục 4:
- `customers` là thực thể trung tâm (gộp leads + customer_accounts cũ).
- Khách không còn tài khoản/mật khẩu; định danh chính là số điện thoại.
- Sale/Admin (`users`) có giải thưởng, phân khu phụ trách và phân quyền n-n.
- Enum lưu dạng string để dễ đọc và dễ migrate.
"""

from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ── Catalog: phân khu và dữ liệu con ─────────────────────────────────────────


class Subdivision(TimestampMixin, Base):
    __tablename__ = "subdivisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    introduction: Mapped[str] = mapped_column(Text)
    location: Mapped[str] = mapped_column(Text)
    # Dữ liệu cleaned_data có mô tả bàn giao dài (>100 ký tự) → 255
    handover_status: Mapped[str] = mapped_column(String(255))
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    display_order: Mapped[int] = mapped_column(default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    apartment_specs: Mapped[list["ApartmentSpec"]] = relationship(
        back_populates="subdivision", cascade="all, delete-orphan"
    )
    amenities: Mapped[list["Amenity"]] = relationship(
        back_populates="subdivision", cascade="all, delete-orphan"
    )
    sales_policies: Mapped[list["SalesPolicy"]] = relationship(
        back_populates="subdivision", cascade="all, delete-orphan"
    )


class ApartmentSpec(Base):
    __tablename__ = "apartment_specs"
    __table_args__ = (UniqueConstraint("subdivision_id", "unit_type"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    subdivision_id: Mapped[int] = mapped_column(ForeignKey("subdivisions.id", ondelete="CASCADE"), index=True)
    unit_type: Mapped[str] = mapped_column(String(50))
    area_min: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    area_max: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    area_note: Mapped[str | None] = mapped_column(String(100))
    price_min: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    price_max: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    price_note: Mapped[str | None] = mapped_column(String(150))
    currency: Mapped[str] = mapped_column(String(10), default="VND")

    subdivision: Mapped[Subdivision] = relationship(back_populates="apartment_specs")


class Amenity(Base):
    __tablename__ = "amenities"

    id: Mapped[int] = mapped_column(primary_key=True)
    subdivision_id: Mapped[int] = mapped_column(ForeignKey("subdivisions.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    scope: Mapped[str] = mapped_column(String(20), index=True)
    description: Mapped[str | None] = mapped_column(Text)

    subdivision: Mapped[Subdivision] = relationship(back_populates="amenities")


class SalesPolicy(TimestampMixin, Base):
    __tablename__ = "sales_policies"

    id: Mapped[int] = mapped_column(primary_key=True)
    subdivision_id: Mapped[int] = mapped_column(ForeignKey("subdivisions.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), default="Chính sách bán hàng")
    policy_content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="published", index=True)

    subdivision: Mapped[Subdivision] = relationship(back_populates="sales_policies")


# ── Sale/Admin: tài khoản, giải thưởng, phân khu phụ trách, phân quyền ────────


user_subdivisions = Table(
    "user_subdivisions",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("subdivision_id", Integer, ForeignKey("subdivisions.id", ondelete="CASCADE"), primary_key=True),
)

user_permissions = Table(
    "user_permissions",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(String(500))
    role: Mapped[str] = mapped_column(String(20), default="sale", index=True)  # admin | sale
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    title: Mapped[str | None] = mapped_column(String(100))  # chức danh, VD "Chuyên viên KD"
    work_shift_start: Mapped[time | None] = mapped_column(Time)
    work_shift_end: Mapped[time | None] = mapped_column(Time)
    join_date: Mapped[date | None] = mapped_column(Date)

    awards: Mapped[list["SaleAward"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", order_by="SaleAward.awarded_at.desc()"
    )
    subdivisions: Mapped[list[Subdivision]] = relationship(secondary=user_subdivisions)
    permissions: Mapped[list["Permission"]] = relationship(secondary=user_permissions)


class SaleAward(Base):
    __tablename__ = "sale_awards"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    award_name: Mapped[str] = mapped_column(String(255))
    awarded_at: Mapped[date] = mapped_column(Date)
    note: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="awards")


class Permission(Base):
    """Danh mục chức năng (master list) cho menu Phân quyền."""

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)  # VD customer.view_all
    name: Mapped[str] = mapped_column(String(255))
    group_name: Mapped[str] = mapped_column(String(100))  # nhóm menu, VD "Khách hàng"


# ── Khách hàng (thực thể trung tâm) ──────────────────────────────────────────


class Customer(TimestampMixin, Base):
    """Khách hàng — gộp `leads` + `customer_accounts` cũ (quyết định D2).

    Định danh chính là `phone`. Khách chat ẩn danh qua session_id, chỉ trở
    thành Customer khi để lại tên + SĐT (lead capture) hoặc điền form liên hệ.
    """

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255))
    # AI phân loại: real_need | investor | ghost | unknown
    customer_type: Mapped[str] = mapped_column(String(20), default="unknown", index=True)
    # AI chấm nhiệt độ: hot | warm | cold | unknown
    temperature: Mapped[str] = mapped_column(String(10), default="unknown", index=True)
    lead_score: Mapped[int | None] = mapped_column(Integer)  # 0-100, dẫn ra temperature
    # Pipeline CRM: new | contacted | consulting | visiting | won | lost
    status: Mapped[str] = mapped_column(String(20), default="new", index=True)
    interested_subdivision_id: Mapped[int | None] = mapped_column(
        ForeignKey("subdivisions.id", ondelete="SET NULL"), index=True
    )
    preferred_unit_type: Mapped[str | None] = mapped_column(String(50))
    budget_min: Mapped[int | None] = mapped_column(BigInteger)  # VND
    budget_max: Mapped[int | None] = mapped_column(BigInteger)  # VND
    purpose: Mapped[str] = mapped_column(String(20), default="unknown")  # to_live | to_invest | unknown
    needs_summary: Mapped[str | None] = mapped_column(Text)
    assigned_sale_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    source: Mapped[str] = mapped_column(String(30), default="chat")  # chat | contact_form | manual
    consent_contact: Mapped[bool] = mapped_column(Boolean, default=False)
    last_contact_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    assigned_sale: Mapped[User | None] = relationship()
    interested_subdivision: Mapped[Subdivision | None] = relationship()
    notes: Mapped[list["CustomerNote"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan", order_by="CustomerNote.created_at"
    )
    purchases: Mapped[list["PurchaseHistory"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan", order_by="PurchaseHistory.purchase_date.desc()"
    )
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="customer")


class CustomerNote(Base):
    __tablename__ = "customer_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    customer: Mapped[Customer] = relationship(back_populates="notes")
    author: Mapped[User | None] = relationship()


class PurchaseHistory(Base):
    """Lịch sử mua nhà của khách: phân khu, loại căn, thời gian, giá, sale phụ trách."""

    __tablename__ = "purchase_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    subdivision_id: Mapped[int] = mapped_column(ForeignKey("subdivisions.id", ondelete="RESTRICT"), index=True)
    unit_type: Mapped[str] = mapped_column(String(50))
    purchase_date: Mapped[date] = mapped_column(Date)
    price: Mapped[int] = mapped_column(BigInteger)  # VND
    responsible_sale_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="deposit")  # deposit | contract | handed_over
    note: Mapped[str | None] = mapped_column(Text)

    customer: Mapped[Customer] = relationship(back_populates="purchases")
    subdivision: Mapped[Subdivision] = relationship()
    responsible_sale: Mapped[User | None] = relationship()


# ── Hội thoại chat ───────────────────────────────────────────────────────────


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"), index=True
    )
    subdivision_id: Mapped[int | None] = mapped_column(ForeignKey("subdivisions.id", ondelete="SET NULL"))
    user_message_count: Mapped[int] = mapped_column(Integer, default=0)  # phục vụ chặn FREE_MESSAGE_LIMIT
    is_lead_captured: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_message_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    messages: Mapped[list["Message"]] = relationship(
        cascade="all, delete-orphan", order_by="Message.created_at"
    )
    customer: Mapped[Customer | None] = relationship(back_populates="conversations")


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (Index("ix_messages_conversation_created", "conversation_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20))  # user | ai | system
    content: Mapped[str] = mapped_column(Text)
    meta: Mapped[dict | None] = mapped_column(JSON)  # citations, detected_intent, score_delta...
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ── Fallback rules ───────────────────────────────────────────────────────────


class FallbackRule(TimestampMixin, Base):
    __tablename__ = "fallback_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), unique=True)
    response_message: Mapped[str] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
