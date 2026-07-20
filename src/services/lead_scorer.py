"""Service chấm điểm Lead dựa trên lịch sử chat và user profile.

Gọi LLM để phân loại HOT / WARM / COLD, sinh điểm số 0-100 và đưa ra lý do.
Nếu LLM lỗi hoặc trả JSON không hợp lệ, service rơi về rubric rule-based để
lead/ticket không bị mất.
"""

from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from src.services.llm import get_llm

TICKET_SCORE_THRESHOLD = 70
WARM_SCORE_THRESHOLD = 40

SCORING_PROMPT = """Bạn là chuyên gia phân tích chất lượng lead bất động sản.

Phân tích lịch sử chat và profile khách hàng dưới đây, sau đó đánh giá mức độ tiềm năng.

**Rubric chấm điểm 0-100:**
- Ngân sách và mức phù hợp tài chính (0-30): rõ ngân sách, đủ khả năng mua căn Ocean Park, mức >= 2 tỷ là tín hiệu tốt.
- Thời gian/độ khẩn cấp (0-20): muốn mua ngay/trong 3 tháng cao hơn chỉ tham khảo.
- Mục đích mua (0-15): ở thật, đầu tư, cho thuê, mua cho gia đình càng rõ càng tốt.
- Loại căn/nhu cầu sản phẩm (0-10): đã nói rõ studio/1PN/2PN/3PN, phân khu, mã căn.
- Bối cảnh gia đình/life stage (0-10): vợ chồng trẻ, mới cưới, có con, chuyển nhà, gần trường/làm việc.
- Sẵn sàng liên hệ sales (0-15): để lại SĐT, hỏi gặp sales, hỏi cọc, lịch xem nhà, quỹ căn thật.

**Quy đổi:**
- HOT: numeric_score >= 70 hoặc có tín hiệu mua rất rõ.
- WARM: numeric_score 40-69, có nhu cầu nhưng chưa đủ tín hiệu chốt.
- COLD: numeric_score < 40, chỉ tìm hiểu chung.
- handover_recommended=true khi numeric_score >= 70 hoặc khách chủ động muốn gặp Sales.

**Dữ liệu:**
{data}

**Yêu cầu output (JSON thuần túy, không markdown):**
{{
  "score": "HOT" | "WARM" | "COLD",
  "numeric_score": 0-100,
  "handover_recommended": true | false,
  "score_reason": "Lý do ngắn gọn 1-2 câu bằng tiếng Việt",
  "breakdown": {{
    "budget": 0-30,
    "timeline": 0-20,
    "purpose": 0-15,
    "unit_type": 0-10,
    "life_stage": 0-10,
    "contact_readiness": 0-15
  }}
}}"""


async def score_lead(
    chat_history: list[dict],
    user_profile: dict,
    name: str,
) -> tuple[str, str]:
    """Chấm điểm lead. Trả về (score, score_reason)."""
    detail = await score_lead_detail(chat_history, user_profile, name)
    return detail["score"], detail["score_reason"]


async def score_lead_detail(
    chat_history: list[dict],
    user_profile: dict,
    name: str,
) -> dict[str, Any]:
    """Chấm điểm lead chi tiết để dùng cho CRM ticket và admin dashboard."""
    recent_messages = chat_history[-20:] if len(chat_history) > 20 else chat_history
    chat_summary = "\n".join(
        f"[{m.get('role', 'user').upper()}]: {m.get('content', '')[:200]}"
        for m in recent_messages
    )

    data = {
        "customer_name": name,
        "chat_summary": chat_summary or "(Không có lịch sử chat)",
        "budget": user_profile.get("budget_raw") or user_profile.get("budget"),
        "unit_type": user_profile.get("unit_type"),
        "purpose": user_profile.get("purpose"),
        "timeline": user_profile.get("timeline"),
        "family_size": user_profile.get("family_size"),
        "life_stage": user_profile.get("life_stage"),
        "manual_sales_request": bool(user_profile.get("manual_sales_request")),
        "notes": user_profile.get("notes"),
    }

    try:
        llm = get_llm(temperature=0.2)
        prompt = SCORING_PROMPT.format(data=json.dumps(data, ensure_ascii=False, indent=2))

        response = await llm.ainvoke([
            SystemMessage(content="Bạn là AI chấm điểm lead bất động sản. Chỉ trả về JSON."),
            HumanMessage(content=prompt),
        ])

        content = response.content.strip()
        import re
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            json_str = match.group(0)
        else:
            json_str = content

        result = json.loads(json_str)
        return _normalize_scoring_result(result, user_profile)

    except Exception:
        import logging
        logging.getLogger(__name__).exception("Lead scoring LLM error for %s", name)
        fallback = _rule_based_detail(user_profile)
        fallback["score_reason"] = (
            "(Auto-scored) Không thể kết nối AI. "
            "Đã dùng rubric chấm điểm dự phòng."
        )
        return fallback


def _rule_based_score(user_profile: dict) -> str:
    """Fallback scoring không cần LLM."""
    return _rule_based_detail(user_profile)["score"]


def _rule_based_detail(user_profile: dict) -> dict[str, Any]:
    """Fallback scoring có breakdown, không cần LLM."""
    budget = int(user_profile.get("budget") or 0)
    has_purpose = bool(user_profile.get("purpose"))
    has_unit_type = bool(user_profile.get("unit_type"))
    timeline = str(user_profile.get("timeline") or "").lower()
    notes = str(user_profile.get("notes") or "").lower()
    life_stage = str(user_profile.get("life_stage") or "").lower()
    manual_sales_request = bool(user_profile.get("manual_sales_request"))

    breakdown = {
        "budget": _budget_points(budget),
        "timeline": _timeline_points(timeline),
        "purpose": 15 if has_purpose else 0,
        "unit_type": 10 if has_unit_type else 0,
        "life_stage": _life_stage_points(life_stage, user_profile),
        "contact_readiness": _contact_readiness_points(notes, manual_sales_request),
    }
    numeric_score = min(100, sum(breakdown.values()))

    if numeric_score >= TICKET_SCORE_THRESHOLD:
        score = "HOT"
    elif numeric_score >= WARM_SCORE_THRESHOLD:
        score = "WARM"
    else:
        score = "COLD"

    if budget >= 3_000_000_000 and has_purpose:
        score = "HOT"
        numeric_score = max(numeric_score, TICKET_SCORE_THRESHOLD)
    elif budget >= 1_500_000_000 or (has_purpose and has_unit_type):
        score = "WARM" if score == "COLD" else score
        numeric_score = max(numeric_score, WARM_SCORE_THRESHOLD)

    return {
        "score": score,
        "numeric_score": numeric_score,
        "handover_recommended": manual_sales_request or numeric_score >= TICKET_SCORE_THRESHOLD,
        "score_reason": _rule_based_reason(score, numeric_score, user_profile),
        "breakdown": breakdown,
    }


def _normalize_scoring_result(result: dict[str, Any], user_profile: dict) -> dict[str, Any]:
    fallback = _rule_based_detail(user_profile)

    score = str(result.get("score") or fallback["score"]).upper()
    numeric_score = _coerce_int(result.get("numeric_score"), fallback["numeric_score"])
    numeric_score = max(0, min(100, numeric_score))

    if score not in ("HOT", "WARM", "COLD"):
        score = _score_from_numeric(numeric_score) if "numeric_score" in result else "WARM"

    breakdown = result.get("breakdown")
    if not isinstance(breakdown, dict):
        breakdown = fallback["breakdown"]
    else:
        breakdown = {
            "budget": max(0, min(30, _coerce_int(breakdown.get("budget"), 0))),
            "timeline": max(0, min(20, _coerce_int(breakdown.get("timeline"), 0))),
            "purpose": max(0, min(15, _coerce_int(breakdown.get("purpose"), 0))),
            "unit_type": max(0, min(10, _coerce_int(breakdown.get("unit_type"), 0))),
            "life_stage": max(0, min(10, _coerce_int(breakdown.get("life_stage"), 0))),
            "contact_readiness": max(0, min(15, _coerce_int(breakdown.get("contact_readiness"), 0))),
        }

    handover_recommended = bool(result.get("handover_recommended"))
    if numeric_score >= TICKET_SCORE_THRESHOLD or user_profile.get("manual_sales_request"):
        handover_recommended = True

    return {
        "score": score,
        "numeric_score": numeric_score,
        "handover_recommended": handover_recommended,
        "score_reason": result.get("score_reason") or fallback["score_reason"],
        "breakdown": breakdown,
    }


def _score_from_numeric(numeric_score: int) -> str:
    if numeric_score >= TICKET_SCORE_THRESHOLD:
        return "HOT"
    if numeric_score >= WARM_SCORE_THRESHOLD:
        return "WARM"
    return "COLD"


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _budget_points(budget: int) -> int:
    if budget >= 3_000_000_000:
        return 30
    if budget >= 2_000_000_000:
        return 24
    if budget >= 1_500_000_000:
        return 16
    if budget > 0:
        return 8
    return 0


def _timeline_points(timeline: str) -> int:
    if not timeline:
        return 0
    if any(term in timeline for term in ("ngay", "tuần", "tháng này", "1 tháng", "lập tức")):
        return 20
    if any(term in timeline for term in ("2 tháng", "3 tháng", "quý", "sớm")):
        return 16
    if any(term in timeline for term in ("6 tháng", "năm nay")):
        return 8
    return 5


def _life_stage_points(life_stage: str, user_profile: dict) -> int:
    family_size = int(user_profile.get("family_size") or 0)
    if family_size >= 2:
        return 10
    if any(term in life_stage for term in ("vợ chồng", "mới cưới", "có con", "gia đình")):
        return 10
    return 0


def _contact_readiness_points(notes: str, manual_sales_request: bool) -> int:
    if manual_sales_request:
        return 15
    if any(term in notes for term in ("gặp sales", "tư vấn viên", "gọi", "liên hệ", "đặt cọc", "xem nhà")):
        return 15
    return 0


def _rule_based_reason(score: str, numeric_score: int, user_profile: dict) -> str:
    if score == "HOT":
        return f"Khách có tín hiệu mua rõ, điểm rubric {numeric_score}/100 nên cần chuyển Sales ưu tiên."
    if score == "WARM":
        return f"Khách có một số tín hiệu nhu cầu, điểm rubric {numeric_score}/100 nhưng cần khai thác thêm."
    return "Khách mới ở giai đoạn tìm hiểu, chưa đủ dữ liệu về ngân sách, thời gian hoặc nhu cầu cụ thể."
