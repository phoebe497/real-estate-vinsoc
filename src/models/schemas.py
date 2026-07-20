"""Pydantic schemas V2 cho FastAPI request/response validation.

Nhóm schema theo BAN_THIET_KE_V2.md Mục 6.5 (chat contract) và Mục 8 (API).
"""

from __future__ import annotations

import re
import uuid
from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# ── Helpers ──────────────────────────────────────────────────────────────────


def _validate_vn_phone(value: str) -> str:
    cleaned = re.sub(r"[\s\-\.]", "", value)
    cleaned = re.sub(r"^\+84", "0", cleaned)
    if not re.match(r"^0[3-9]\d{8}$", cleaned):
        raise ValueError("Số điện thoại không hợp lệ")
    return cleaned


# ── Chat / Agent ─────────────────────────────────────────────────────────────


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1, max_length=10_000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1)
    session_id: str | None = Field(default=None, min_length=36, max_length=36)

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            return str(uuid.UUID(value))
        except ValueError as exc:
            raise ValueError("session_id must be a UUID") from exc


class ZoneMatch(BaseModel):
    name: str
    slug: str
    match_reason: str
    price_range: str = ""
    design_style: str = ""


class Citation(BaseModel):
    citation_id: str = Field(default="", description="Rendered citation number, e.g. 1")
    chunk_id: str = Field(default="", description="Retrieved chunk id")
    document_id: str = Field(default="", description="Source document id")
    title: str = Field(default="", description="Display title")
    source_url: str = Field(default="", description="Trusted internal or allowed source URL")
    source_type: str = Field(default="knowledge_chunk", description="Source type")
    domain: str = Field(default="general", description="Knowledge domain")
    confidence_level: str = Field(default="medium", description="Source confidence")
    data_period: str = Field(default="", description="Data period or effective period")
    relevance_score: float = Field(default=0.0, description="Retriever relevance score")
    source_id: str = Field(default="", description="Backward-compatible source/chunk id")
    snippet: str = Field(default="", description="Short source excerpt")


class DetectedProfile(BaseModel):
    """Kết quả phân loại/chấm điểm của agent sau mỗi lượt chat (Mục 6.5)."""

    customer_type: str = "unknown"  # real_need | investor | ghost | unknown
    temperature: str = "unknown"    # hot | warm | cold | unknown
    lead_score: int | None = None
    interested_subdivision: str | None = None
    budget_range: list[int | None] = Field(default_factory=lambda: [None, None])
    unit_type: str | None = None


class ChatResponse(BaseModel):
    status: str = Field(default="ok", description="ok | insufficient_context | safe_rewrite")
    # `reply` là tên chuẩn V2; `response` giữ để FE cũ không gãy trong lúc chuyển đổi.
    reply: str = Field(default="", description="AI reply (V2 contract)")
    response: str = Field(..., description="AI response (legacy alias of reply)")
    require_lead_capture: bool = Field(default=False)
    trigger_handover: bool = Field(default=False)
    recommended_zones: list[ZoneMatch] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    detected: DetectedProfile | None = None
    session_id: str
    analysis: str = ""


class UserProfile(BaseModel):
    budget: int | None = None
    unit_type: str | None = None
    purpose: str | None = None
    timeline: str | None = None
    family_size: int | None = None
    life_stage: str | None = None
    notes: str = ""


class RecommendRequest(BaseModel):
    budget: int | None = None
    unit_type: str | None = None
    purpose: str | None = None
    top_k: int = Field(default=3, ge=1, le=10)


class RecommendZone(BaseModel):
    name: str
    slug: str
    match_reason: str
    price_range: str
    design_style: str
    score: float
    unit_types: list[str] = Field(default_factory=list)
    target_audience: list[str] = Field(default_factory=list)
    handover_status: str = ""


class RecommendResponse(BaseModel):
    total: int
    recommendations: list[RecommendZone]


class CustomerScoreRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=8, max_length=20)
    email: str | None = Field(None, max_length=200)
    chat_history: list[ChatMessage] = Field(default_factory=list)
    user_profile: UserProfile = Field(default_factory=UserProfile)
    session_id: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_vn_phone(cls, v: str) -> str:
        return _validate_vn_phone(v)


class CustomerScoreResponse(BaseModel):
    score: Literal["HOT", "WARM", "COLD"]
    numeric_score: int = Field(default=0, ge=0, le=100)
    score_reason: str
    scoring_breakdown: dict[str, int] = Field(default_factory=dict)
    handover_recommended: bool = False
    name: str
    phone: str


# ── Catalog ──────────────────────────────────────────────────────────────────


class ApartmentSpecResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    unit_type: str
    area_min: float | None
    area_max: float | None
    area_note: str | None
    price_min: float | None
    price_max: float | None
    price_note: str | None
    currency: str


class AmenityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    scope: str
    description: str | None


class SalesPolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    policy_content: str
    status: str


class SubdivisionSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    introduction: str
    location: str
    handover_status: str
    thumbnail_url: str | None


class SubdivisionDetailResponse(SubdivisionSummaryResponse):
    apartment_specs: list[ApartmentSpecResponse] = Field(default_factory=list)
    amenities: list[AmenityResponse] = Field(default_factory=list)
    sales_policies: list[SalesPolicyResponse] = Field(default_factory=list)


class SubdivisionBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str


# ── Auth / Sale / Admin ──────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    phone: str | None = None
    role: str
    is_active: bool
    avatar_url: str | None = None
    title: str | None = None
    work_shift_start: time | None = None
    work_shift_end: time | None = None
    join_date: date | None = None


class MeResponse(BaseModel):
    user: UserResponse
    permissions: list[str] = Field(default_factory=list)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ProfileUpdateRequest(BaseModel):
    """Sale tự sửa profile cá nhân (PATCH /auth/me)."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    avatar_url: str | None = Field(default=None, max_length=500)
    title: str | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class SaleAwardCreateRequest(BaseModel):
    award_name: str = Field(min_length=1, max_length=255)
    awarded_at: date
    note: str | None = None


class SaleAwardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    award_name: str
    awarded_at: date
    note: str | None


class SaleCreateRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: Literal["admin", "sale"] = "sale"
    phone: str | None = Field(default=None, max_length=20)
    title: str | None = Field(default=None, max_length=100)
    avatar_url: str | None = Field(default=None, max_length=500)
    work_shift_start: time | None = None
    work_shift_end: time | None = None
    join_date: date | None = None


class SaleUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    title: str | None = Field(default=None, max_length=100)
    avatar_url: str | None = Field(default=None, max_length=500)
    work_shift_start: time | None = None
    work_shift_end: time | None = None
    join_date: date | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class SaleResponse(UserResponse):
    subdivisions: list[SubdivisionBrief] = Field(default_factory=list)
    awards: list[SaleAwardResponse] = Field(default_factory=list)
    assigned_customer_count: int = 0
    sold_count: int = 0


class SaleSubdivisionsUpdateRequest(BaseModel):
    subdivision_ids: list[int] = Field(default_factory=list)


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    group_name: str


class UserPermissionsUpdateRequest(BaseModel):
    codes: list[str] = Field(default_factory=list)


class UserStatusUpdateRequest(BaseModel):
    is_active: bool


# ── Customers (CRM) ──────────────────────────────────────────────────────────


CustomerStatus = Literal["new", "contacted", "consulting", "visiting", "won", "lost"]
CustomerType = Literal["real_need", "investor", "ghost", "unknown"]
Temperature = Literal["hot", "warm", "cold", "unknown"]
Purpose = Literal["to_live", "to_invest", "unknown"]


class CustomerCaptureRequest(BaseModel):
    """Form 'Tạo đơn tư vấn' / lead capture trong chat (Mục 5.1-5.2)."""

    full_name: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=8, max_length=20)
    email: EmailStr | None = None
    session_id: str | None = None
    interested_subdivision_slug: str | None = Field(default=None, max_length=100)
    preferred_unit_type: str | None = Field(default=None, max_length=50)
    budget_min: int | None = Field(default=None, ge=0)
    budget_max: int | None = Field(default=None, ge=0)
    purpose: Purpose = "unknown"
    contact_time: str | None = Field(default=None, max_length=255)
    note: str | None = Field(default=None, max_length=2000)
    consent_contact: bool = True

    @field_validator("phone")
    @classmethod
    def validate_vn_phone(cls, v: str) -> str:
        return _validate_vn_phone(v)


class CustomerCaptureResponse(BaseModel):
    customer_id: int
    message: str = "Cảm ơn Anh/Chị! Sales sẽ liên hệ trong thời gian sớm nhất."


class ContactRequest(BaseModel):
    """Form liên hệ ở trang public (POST /api/v1/contact)."""

    name: str | None = Field(default=None, max_length=255)
    phone: str = Field(min_length=8, max_length=20)
    email: EmailStr | None = None
    preferred_bedrooms: str | None = Field(default=None, max_length=50)
    message: str | None = Field(default=None, max_length=2000)
    subdivision_slug: str | None = Field(default=None, max_length=100)


class CustomerNoteCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CustomerNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    created_at: datetime
    author: UserResponse | None = None


class PurchaseCreateRequest(BaseModel):
    subdivision_id: int
    unit_type: str = Field(min_length=1, max_length=50)
    purchase_date: date
    price: int = Field(ge=0)
    responsible_sale_id: int | None = None
    status: Literal["deposit", "contract", "handed_over"] = "deposit"
    note: str | None = None


class PurchaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subdivision: SubdivisionBrief
    unit_type: str
    purchase_date: date
    price: int
    responsible_sale: UserResponse | None = None
    status: str
    note: str | None


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str | None
    phone: str
    email: str | None
    customer_type: str
    temperature: str
    lead_score: int | None
    status: str
    interested_subdivision: SubdivisionBrief | None = None
    preferred_unit_type: str | None
    budget_min: int | None
    budget_max: int | None
    purpose: str
    needs_summary: str | None
    assigned_sale: UserResponse | None = None
    source: str
    consent_contact: bool
    last_contact_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CustomerDetailResponse(CustomerResponse):
    notes: list[CustomerNoteResponse] = Field(default_factory=list)
    purchases: list[PurchaseResponse] = Field(default_factory=list)


class CustomerUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    customer_type: CustomerType | None = None
    temperature: Temperature | None = None
    status: CustomerStatus | None = None
    interested_subdivision_id: int | None = None
    preferred_unit_type: str | None = Field(default=None, max_length=50)
    budget_min: int | None = Field(default=None, ge=0)
    budget_max: int | None = Field(default=None, ge=0)
    purpose: Purpose | None = None
    needs_summary: str | None = None
    consent_contact: bool | None = None
    last_contact_at: datetime | None = None


class CustomerAssignRequest(BaseModel):
    sale_id: int | None = None  # None = bỏ phân công


# ── Conversations / Messages ─────────────────────────────────────────────────


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    meta: dict | None = None
    created_at: datetime


class ConversationSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    customer_id: int | None
    subdivision_id: int | None
    user_message_count: int
    is_lead_captured: bool
    started_at: datetime
    last_message_at: datetime


class ConversationDetailResponse(ConversationSummaryResponse):
    messages: list[MessageResponse] = Field(default_factory=list)


# ── Fallback rules ───────────────────────────────────────────────────────────


class FallbackRuleRequest(BaseModel):
    keyword: str = Field(min_length=1, max_length=255)
    response_message: str = Field(min_length=1, max_length=2000)
    priority: int = 0
    is_active: bool = True


class FallbackRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    keyword: str
    response_message: str
    priority: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ── Dashboard (Mục 11) ───────────────────────────────────────────────────────


class BreakdownItem(BaseModel):
    label: str
    count: int


class SalePerformanceItem(BaseModel):
    id: int
    name: str
    assigned_count: int = 0
    sold_count: int = 0


class DashboardStatsResponse(BaseModel):
    total_customers: int = 0
    new_today: int = 0
    new_this_week: int = 0
    new_this_month: int = 0
    conversations: int = 0
    messages: int = 0
    captured_conversations: int = 0
    capture_rate: float = 0.0
    handover_customers: int = 0
    active_fallback_rules: int = 0
    customer_type_breakdown: list[BreakdownItem] = Field(default_factory=list)
    temperature_breakdown: list[BreakdownItem] = Field(default_factory=list)
    status_funnel: list[BreakdownItem] = Field(default_factory=list)
    top_subdivisions: list[BreakdownItem] = Field(default_factory=list)
    customer_trend: list[BreakdownItem] = Field(default_factory=list)
    sales_performance: list[SalePerformanceItem] = Field(default_factory=list)
