"""Profile Node — phân loại khách & chấm nhiệt độ lead (BAN_THIET_KE_V2 Mục 6.3).

Chạy sau rag_node, trước answer/llm_node. Rule-based, deterministic:
- `lead_score` (0-100) cộng dồn theo hội thoại; delta mỗi lượt lưu vào
  `detected.score_delta` để truy vết qua messages.meta.
- `temperature`: hot ≥ 55, warm 25-54, cold < 25.
- `customer_type`: real_need | investor | ghost | unknown theo tín hiệu keyword.

LLM structured-output có thể bổ sung sau; lớp rule-based này chạy mỗi lượt
không tốn thêm latency/chi phí LLM.
"""

from __future__ import annotations

import logging
import re
import unicodedata

from src.agents.state import AgentState, get_last_user_message
from src.services.vinhomes_data import get_all_zones

HOT_THRESHOLD = 55
WARM_THRESHOLD = 25


def _normalize(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text.lower()).strip()


# Tín hiệu rubric (regex trên text đã bỏ dấu)
_VISIT_RE = re.compile(r"xem nha|xem can|di xem|dat lich|hen lich|tham quan|nha mau|xem thuc te")
_MEET_SALE_RE = re.compile(r"gap sale|gap sales|goi lai|goi cho toi|lien he (?:toi|minh|em|anh|chi)|gap (?:nhan vien|chuyen vien|tu van)|noi chuyen voi (?:sale|nhan vien)")
_DEPOSIT_RE = re.compile(r"dat coc|booking|giu cho|ky hop dong|chot can|chot mua|thanh toan")
_BUDGET_RE = re.compile(r"\d+(?:[.,]\d+)?\s*(?:ty|ti|trieu)|ngan sach|tam gia|khoang gia|tai chinh")
_DETAIL_RE = re.compile(r"tien do|ban giao|tien ich|truong hoc|truong|benh vien|ho boi|cong vien|phap ly|so hong|di chuyen|vi tri")

_INVESTOR_RE = re.compile(r"dau tu|cho thue|roi|loi nhuan|tang gia|luot song|thanh khoan|sinh loi|ty suat|dong tien")
_REAL_NEED_RE = re.compile(r"de o|o thuc|o that|an cu|gia dinh|con (?:nho|hoc|di hoc)|truong|chuyen ve|don ve|di lam|vo chong|ket hon")

_REAL_ESTATE_ANY_RE = re.compile(
    r"can ho|chung cu|phan khu|\bgia\b|\bty\b|trieu|\bmua\b|\bthue\b|\btoa\b|du an|"
    r"ocean park|vinhomes|\d\s*pn|studio|dat coc|xem nha|tien ich|ban giao"
)


def _zone_aliases() -> dict[str, list[str]]:
    aliases: dict[str, list[str]] = {}
    for zone in get_all_zones():
        slug = zone.get("slug", "")
        name = _normalize(zone.get("name", ""))
        alias_list = {name, _normalize(slug.replace("-", " "))}
        # "the zenpark" → thêm "zenpark" để bắt cách gọi tắt
        alias_list.update(a[4:] for a in list(alias_list) if a.startswith("the ") and len(a) > 6)
        aliases[slug] = [a for a in alias_list if len(a) >= 4]
    return aliases


def _zones_mentioned(normalized_text: str) -> set[str]:
    mentioned = set()
    for slug, alias_list in _zone_aliases().items():
        if any(alias in normalized_text for alias in alias_list):
            mentioned.add(slug)
    return mentioned


def compute_score_delta(
    latest_user_text: str,
    history_user_texts: list[str],
    intent: str,
) -> tuple[int, dict[str, int]]:
    """Tính điểm delta cho lượt chat hiện tại theo rubric Mục 6.3."""
    text = _normalize(latest_user_text)
    signals: dict[str, int] = {}

    if _VISIT_RE.search(text):
        signals["visit_request"] = 30
    if _MEET_SALE_RE.search(text):
        signals["meet_sale"] = 25
    if _DEPOSIT_RE.search(text):
        signals["deposit_intent"] = 25
    if _BUDGET_RE.search(text):
        signals["budget_discussed"] = 10

    zones_now = _zones_mentioned(text)
    if len(zones_now) >= 2:
        signals["zone_comparison"] = 8

    # Tập trung sâu vào MỘT phân khu: nhắc lại phân khu đã hỏi trước đó
    if len(zones_now) == 1:
        zone = next(iter(zones_now))
        previous_mentions = sum(
            1 for old in history_user_texts[:-1] if zone in _zones_mentioned(_normalize(old))
        )
        if previous_mentions >= 1:
            signals["zone_focus"] = 15

    if _DETAIL_RE.search(text) and "visit_request" not in signals:
        signals["detail_question"] = 5

    if intent == "out_of_scope":
        signals["off_topic"] = -10
    elif not signals and intent not in ("greeting", "handover") and not zones_now:
        signals["generic_question"] = -5

    return sum(signals.values()), signals


def temperature_for(score: int) -> str:
    if score >= HOT_THRESHOLD:
        return "hot"
    if score >= WARM_THRESHOLD:
        return "warm"
    return "cold"


def classify_customer_type(user_texts: list[str]) -> str:
    """Phân loại real_need / investor / ghost / unknown theo tín hiệu keyword."""
    if not user_texts:
        return "unknown"
    combined = _normalize(" \n ".join(user_texts))
    investor_hits = len(_INVESTOR_RE.findall(combined))
    real_need_hits = len(_REAL_NEED_RE.findall(combined))

    if investor_hits or real_need_hits:
        return "investor" if investor_hits > real_need_hits else "real_need"

    # Ghost: nhiều tin nhưng không có tin nào dính từ khóa bất động sản
    if len(user_texts) >= 3:
        relevant = sum(1 for t in user_texts if _REAL_ESTATE_ANY_RE.search(_normalize(t)))
        if relevant / len(user_texts) < 0.4:
            return "ghost"
    return "unknown"


async def profile_node(state: AgentState) -> dict:
    """LangGraph node: cập nhật detected profile (loại khách, nhiệt độ, điểm)."""
    latest = get_last_user_message(state.get("messages", []))
    history = state.get("profile_messages", state.get("messages", []))
    user_texts = [m.get("content", "") for m in history if m.get("role") == "user"]
    if not user_texts or user_texts[-1] != latest:
        user_texts.append(latest)

    intent = state.get("intent", "consult")
    current_score = int(state.get("current_lead_score") or 0)

    delta, signals = compute_score_delta(latest, user_texts, intent)
    score = max(0, min(100, current_score + delta))

    profile = state.get("user_profile", {}) or {}
    budget = profile.get("budget")
    recommended = state.get("recommended_zones", [])
    interested = recommended[0]["slug"] if recommended else None
    if interested is None:
        zones_now = _zones_mentioned(_normalize(latest))
        interested = next(iter(zones_now)) if len(zones_now) == 1 else None

    detected = {
        "customer_type": classify_customer_type(user_texts),
        "temperature": temperature_for(score),
        "lead_score": score,
        "score_delta": delta,
        "signals": signals,
        "interested_subdivision": interested,
        "budget_range": [budget, budget] if budget else [None, None],
        "unit_type": profile.get("unit_type"),
    }
    logging.getLogger("agent.profile_node").info(
        "[profile_node] session=%s score=%d(+%d) temperature=%s type=%s signals=%s",
        state.get("session_id", "?"),
        score,
        delta,
        detected["temperature"],
        detected["customer_type"],
        signals,
    )
    return {"detected": detected}
