"""AgentState mở rộng cho Vinhomes AI Advisor.

State được truyền qua tất cả LangGraph nodes.
total=False cho phép tất cả fields là optional trong TypedDict.
"""

from __future__ import annotations

from typing import Any, TypedDict


class Message(TypedDict):
    role: str   # "user" | "assistant" | "system"
    content: str


class UserProfile(TypedDict, total=False):
    """Profile khách hàng được extract dần từ hội thoại."""
    budget: int | None          # Ngân sách (VNĐ)
    budget_raw: str | None      # Nguyên văn ngân sách khách nói ("3 tỷ", "2.5B")
    unit_type: str | None       # "1PN", "2PN", "3PN", "Studio"
    purpose: str | None         # "ở thật", "đầu tư", "cho thuê", "nghỉ dưỡng"
    timeline: str | None        # "ngay", "3 tháng", "cuối năm"
    family_size: int | None     # Số người trong gia đình
    school_need: bool | None    # Có nhu cầu gần trường/tiện ích cho con
    notes: str                  # Ghi chú thêm từ hội thoại


class ZoneMatch(TypedDict):
    name: str
    slug: str
    match_reason: str
    price_range: str
    design_style: str


class Citation(TypedDict, total=False):
    citation_id: str
    chunk_id: str
    document_id: str
    title: str
    source_url: str
    source_type: str
    source_id: str
    domain: str
    snippet: str
    confidence_level: str
    data_period: str
    relevance_score: float


class AgentState(TypedDict, total=False):
    """State schema cho Vinhomes LangGraph agent.

    Lifecycle:
      query → intent_node → [rag_node → llm_node] hoặc [handover]
    """

    # Input
    messages: list[Message]     # Toàn bộ lịch sử chat (user + assistant)
    profile_messages: list[Message]  # Lịch sử chỉ dùng để extract nhu cầu/profile, không ép LLM trả lời lại
    session_id: str             # UUID để track session
    current_lead_score: int     # Điểm lead hiện tại (cộng dồn qua các lượt)

    # Processed by intent_node
    intent: str                 # "consult" | "handover" | "price_query" | "greeting"
    trigger_handover: bool      # True nếu cần chuyển Sales

    # Processed by profile_extract (chạy trong intent_node)
    user_profile: UserProfile

    # Processed by rag_node
    zone_context: str           # Context text về phân khu phù hợp (cho LLM)
    recommended_zones: list[ZoneMatch]
    citations: list[Citation]
    retrieved_chunks: list[Any]
    retrieval_debug: dict[str, Any]
    citation_debug: dict[str, Any]
    status: str

    # Processed by profile_node (Mục 6.3)
    detected: dict[str, Any]    # customer_type, temperature, lead_score, score_delta...

    # Final output from llm_node
    response: str               # AI response text

    # Metadata
    error: str | None
    metadata: dict[str, Any]


def get_last_user_message(messages: list[dict]) -> str:
    """Lấy nội dung tin nhắn cuối cùng của user từ danh sách messages."""
    return next(
        (m["content"] for m in reversed(messages) if m.get("role") == "user"),
        "",
    )
