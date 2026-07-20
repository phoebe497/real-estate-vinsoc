"""Intent Detection Node — bước đầu tiên trong LangGraph pipeline.

Node này phân tích tin nhắn cuối cùng của user để xác định intent:
- "consult"      → Câu hỏi thông thường về dự án, phân khu, tiện ích
- "handover"     → Yêu cầu mã căn cụ thể, đặt cọc, kiểm tra quỹ căn
- "price_query"  → Hỏi giá → AI trả lời nhưng phải disclaimer "giá tham khảo"
- "greeting"     → Chào hỏi mở đầu
- "zone_match"   → Đủ thông tin để gợi ý phân khu cụ thể

Đồng thời extract user profile (ngân sách, loại căn, mục đích) từ lịch sử chat.
"""

from __future__ import annotations

import logging
import re

from src.agents.state import AgentState, UserProfile, get_last_user_message

# ---- Intent keyword patterns ----

_HANDOVER_PATTERNS = [
    # Explicit sales/contact actions
    r"gặp\s+(sale|sales|nhân viên|chuyên viên|tư vấn viên)",
    r"(sale|sales|nhân viên|chuyên viên)\s+(gọi|liên hệ|tư vấn)",
    r"(gọi|liên hệ|kết nối)\s+(tôi|mình|em|anh|chị|với tôi|với mình)",
    r"để lại\s+(số điện thoại|sđt|phone|thông tin)",
    r"tư vấn trực tiếp",
    r"hẹn\s+(lịch|gặp|xem)",
    r"xem\s+(nhà|căn|căn hộ|thực tế|nhà mẫu)",

    # Buying/closing actions
    r"đặt cọc",
    r"giữ chỗ",
    r"ký hợp đồng",
    r"thanh toán ngay",
    r"mua luôn",
    r"chốt\s+(căn|mua|luôn)",

    # Inventory/final-price requests that need sales confirmation
    r"mã căn",
    r"căn số",
    r"còn căn",
    r"quỹ căn",
    r"căn cụ thể",
    # Hỏi căn theo đặc điểm cụ thể (view/tầng/ban công) = hỏi quỹ căn realtime
    r"căn nào.{0,40}(view|tầng|ban công|góc|đẹp)",
    r"(có )?căn.{0,20}view (hồ|biển|công viên)",
    r"giá chốt",
    r"giá cuối",
    r"giá hiện hành",
    r"bảng hàng",
    r"căn nào còn",
    r"\b[a-zA-Z]\d+-\d+\b",
    r"\b[a-zA-Z]\d+\s*-\s*\d+\b",
    r"\b[a-zA-Z]\d+\.\d+\b",   # pattern như R1.01, S2.12
]

_PRICE_PATTERNS = [
    r"giá bao nhiêu",
    r"bao nhiêu tiền",
    r"giá (khoảng|tầm)",
    r"tổng giá",
    r"giá/m2",
    r"giá m2",
    r"chi phí",
]

_ZONE_MATCH_TRIGGERS = [
    r"phân khu nào",
    r"nên chọn",
    r"phù hợp (với|cho) (tôi|gia đình|mình)",
    r"tư vấn (cho tôi|giúp|giùm)",
    r"chọn (loại|căn|khu) nào",
]

_GREETING_PATTERNS = [
    r"^(xin chào|chào|hello|hi|hey)\b",
    r"^(alo|ơi)\b",
]

_OUT_OF_SCOPE_PATTERNS = [
    # Competitive projects / other projects
    r"vinhomes grand park", r"grand park",
    r"times city", r"time city",
    r"royal city",
    r"vinhomes central park", r"central park",
    r"vinhomes smart city", r"smart city",
    r"vinhomes riverside", r"riverside",
    r"ocean park 2", r"ocean park 3", r"the empire", r"the crown", r"hưng yên",
    r"cổ loa", r"đan phượng",
    r"novaland", r"sun group", r"bình khánh", r"vạn phúc",
    # Non-real estate topics
    r"\bchính trị\b", r"\blịch sử\b", r"\btôn giáo\b", r"\bthời tiết\b",
    r"\blập trình\b", r"\bviết code\b", r"\bthuật toán\b",
    r"\bgame\b", r"\btrò chơi\b", r"\bbóng đá\b", r"\bthể thao\b",
    r"\bca sĩ\b", r"\bdiễn viên\b", r"\bphim ảnh\b", r"\bâm nhạc\b",
    # General non-real estate conversational noise
    r"\blàm toán\b", r"\bgiải bài tập\b", r"\bviết văn\b", r"\blàm thơ\b"
]

_INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"ignore the rules",
    r"system prompt",
    r"bỏ qua (tất cả |mọi |các |những )?(yêu cầu|quy định|nguyên tắc|luật|rule)",
    r"bỏ qua hướng dẫn",
    r"hãy đóng vai",
    r"you are now a",
    r"translate the system prompt",
    r"reveal your system prompt",
    r"tiết lộ system prompt",
    r"tiết lộ prompt",
    r"hãy bỏ qua",
    r"dữ liệu nội bộ",
    r"thông tin nội bộ",
    r"bảng giá nội bộ",
]

# Yêu cầu lộ thông tin cá nhân của khách hàng khác → từ chối vì bảo mật
_PRIVACY_PATTERNS = [
    r"(số điện thoại|sđt|thông tin|email|địa chỉ|danh sách).{0,40}(khách hàng|khách|người)( đã| khác| trước| cũ| mua)",
    r"(khách hàng|khách|người)( đã| khác| trước)? mua.{0,30}(số điện thoại|sđt|thông tin|liên hệ|tên)",
    r"cho (tôi|mình|em|anh|chị) (xem )?(danh sách|thông tin) khách",
]


def _detect_intent(last_user_message: str, messages: list[dict]) -> str:
    """Phân loại intent từ tin nhắn user cuối."""
    if len(last_user_message) > 10000:
        return "out_of_scope"

    msg = last_user_message.lower()

    # Reject / Out of scope guardrails
    for pattern in _INJECTION_PATTERNS:
        if re.search(pattern, msg, re.IGNORECASE):
            return "out_of_scope"

    for pattern in _PRIVACY_PATTERNS:
        if re.search(pattern, msg, re.IGNORECASE):
            return "privacy"

    for pattern in _OUT_OF_SCOPE_PATTERNS:
        if re.search(pattern, msg, re.IGNORECASE):
            return "out_of_scope"

    # Handover triggers — ưu tiên cao nhất
    for pattern in _HANDOVER_PATTERNS:
        if re.search(pattern, msg, re.IGNORECASE):
            return "handover"

    # Greeting (chỉ khi message rất ngắn)
    if len(messages) <= 2 and len(msg.split()) <= 5:
        for pattern in _GREETING_PATTERNS:
            if re.search(pattern, msg, re.IGNORECASE):
                return "greeting"

    # Zone matching triggers
    for pattern in _ZONE_MATCH_TRIGGERS:
        if re.search(pattern, msg, re.IGNORECASE):
            return "zone_match"

    # Price queries
    for pattern in _PRICE_PATTERNS:
        if re.search(pattern, msg, re.IGNORECASE):
            return "price_query"

    return "consult"


def _extract_budget(text: str) -> tuple[int | None, str | None]:
    """Extract ngân sách từ text. Trả về (VNĐ_int, raw_text)."""
    # Patterns: "3 tỷ", "2.5 tỷ", "3B", "3000 triệu", "3,000,000,000"
    patterns = [
        (r"(\d+(?:[.,]\d+)?)\s*tỷ", lambda m: int(float(m.replace(",", ".")) * 1_000_000_000)),
        (r"(\d+(?:[.,]\d+)?)\s*b\b", lambda m: int(float(m.replace(",", ".")) * 1_000_000_000)),
        (r"(\d+(?:[.,]\d+)?)\s*triệu", lambda m: int(float(m.replace(",", ".")) * 1_000_000)),
    ]

    text_lower = text.lower()
    for pattern, converter in patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            raw = match.group(0)
            try:
                amount = converter(match.group(1))
                return amount, raw
            except (ValueError, AttributeError):
                continue
    return None, None


def _extract_unit_type(text: str) -> str | None:
    """Extract loại căn từ text."""
    patterns = {
        r"\bstudio\b": "Studio",
        r"\b1\s*pn\+1\b|\b1\s*phòng\s*ngủ\s*\+\s*1\b": "1PN+1",
        r"\b1\s*pn\b|\b1\s*phòng\s*ngủ\b|\bmột\s*phòng\s*ngủ\b": "1PN",
        r"\b2\s*pn\+1\b|\b2\s*phòng\s*ngủ\s*\+\s*1\b": "2PN+1",
        r"\b2\s*pn\b|\b2\s*phòng\s*ngủ\b|\bhai\s*phòng\s*ngủ\b": "2PN",
        r"\b3\s*pn\b|\b3\s*phòng\s*ngủ\b|\bba\s*phòng\s*ngủ\b": "3PN",
    }
    text_lower = text.lower()
    for pattern, unit in patterns.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            return unit
    return None


def _extract_purpose(text: str) -> str | None:
    """Extract mục đích mua từ text."""
    text_lower = text.lower()
    if any(kw in text_lower for kw in ["đầu tư", "investment", "sinh lời"]):
        return "đầu tư"
    if any(kw in text_lower for kw in ["cho thuê", "airbnb", "rent out"]):
        return "cho thuê"
    if any(kw in text_lower for kw in ["nghỉ dưỡng", "resort", "thư giãn"]):
        return "nghỉ dưỡng"
    if any(kw in text_lower for kw in ["ở thật", "ở", "sống", "định cư", "gia đình ở"]):
        return "ở thật"
    return None


def _build_user_profile(messages: list[dict]) -> UserProfile:
    """Extract user profile từ toàn bộ lịch sử chat."""
    profile: UserProfile = {}

    # Ghép tất cả user messages thành 1 string để extract
    all_user_text = " ".join(
        m["content"] for m in messages if m.get("role") == "user"
    )

    budget, budget_raw = _extract_budget(all_user_text)
    if budget:
        profile["budget"] = budget
        profile["budget_raw"] = budget_raw

    unit_type = _extract_unit_type(all_user_text)
    if unit_type:
        profile["unit_type"] = unit_type

    purpose = _extract_purpose(all_user_text)
    if purpose:
        profile["purpose"] = purpose

    # Family size hints. Use the largest number to avoid reading
    # "gia đình 4 người, có 2 con" as family_size=2.
    family_matches = re.findall(r"(\d+)\s*(người|thành viên|con)", all_user_text.lower())
    if family_matches:
        try:
            profile["family_size"] = max(int(match[0]) for match in family_matches)
        except ValueError:
            pass

    school_terms = ("con nhỏ", "con học", "cấp 1", "cấp 2", "cấp 3", "trường", "vinschool", "học sinh")
    if any(term in all_user_text.lower() for term in school_terms):
        profile["school_need"] = True

    if profile.get("family_size") and profile.get("family_size", 0) >= 3 and not profile.get("purpose"):
        profile["purpose"] = "ở thật"

    profile["notes"] = ""
    return profile


async def intent_node(state: AgentState) -> dict:
    """LangGraph node: phân loại intent + extract user profile."""
    messages = state.get("messages", [])
    profile_messages = state.get("profile_messages", messages)
    if not messages:
        return {"intent": "greeting", "trigger_handover": False, "user_profile": {}}

    # Lấy message cuối của user
    last_user_msg = get_last_user_message(messages)

    intent = _detect_intent(last_user_msg, messages)
    trigger_handover = intent == "handover"
    user_profile = _build_user_profile(profile_messages)

    logging.getLogger("agent.intent_node").info(
        "[intent_node] session=%s intent=%s trigger_handover=%s profile=%s input=%r",
        state.get("session_id", "?"),
        intent,
        trigger_handover,
        {k: v for k, v in user_profile.items() if v},
        last_user_msg[:120],
    )
    return {
        "intent": intent,
        "trigger_handover": trigger_handover,
        "user_profile": user_profile,
    }
