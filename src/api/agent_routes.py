"""Agent API — chat AI với gating lead capture (BAN_THIET_KE_V2 Mục 5-6).

Endpoints:
  POST /agent/chat            → Chat với AI advisor (LangGraph pipeline)
  POST /agent/recommend       → Gợi ý phân khu theo budget / loại căn / mục đích
  POST /agent/customer-score  → Chấm điểm tiềm năng khách hàng (HOT / WARM / COLD)
  GET  /agent/status          → Health-check agent/LLM

Luồng chat (Mục 5.1):
  1. Khách chat ẩn danh qua session_id; mọi hội thoại lưu vào `conversations`.
  2. Mỗi tin của khách tăng `user_message_count`.
  3. Quá FREE_MESSAGE_LIMIT mà chưa để lại thông tin → không gọi LLM,
     trả `require_lead_capture=true` để FE bung form.
  4. Khách submit form qua POST /api/v1/customers/capture → chat tiếp.
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.agents.graph import agent
from src.agents.nodes.profile_node import temperature_for
from src.api.customers import anonymous_score_from_meta, get_or_create_customer_by_phone
from src.api.dependencies import require_permission
from src.config import get_settings
from src.db.session import get_db
from src.models.entities import Conversation, Customer, FallbackRule, Message, Subdivision, User
from src.models.schemas import (
    ChatRequest,
    ChatResponse,
    CustomerScoreRequest,
    CustomerScoreResponse,
    DetectedProfile,
    RecommendRequest,
    RecommendResponse,
    RecommendZone,
    ZoneMatch,
)
from src.services.lead_scorer import score_lead_detail
from src.services.rate_limiter import BoundedSlidingWindowLimiter, client_identifier
from src.services.recommender import get_zone_recommendations
from src.services.sale_assigner import auto_assign_sale

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])

PHONE_RE = re.compile(r"(?:\+84|0)[\s.\-]?[3-9](?:[\s.\-]?\d){8}\b")
NAME_RE = re.compile(
    r"(?:tên|họ tên|mình là|tôi là|em là|anh là|chị là)\s*[:\-]?\s*([A-Za-zÀ-ỹ][A-Za-zÀ-ỹ\s]{1,80})",
    re.IGNORECASE,
)

LEAD_CAPTURE_MESSAGE = (
    "Để tiếp tục được tư vấn chi tiết, Anh/Chị vui lòng để lại họ tên và số điện thoại "
    "qua form 'Tạo đơn tư vấn' ngay trong cửa sổ chat. Sau khi gửi thông tin, "
    "em sẽ tiếp tục hỗ trợ Anh/Chị ngay ạ!"
)

RATE_LIMIT_MESSAGE = (
    "Hệ thống đang nhận được rất nhiều câu hỏi. Vui lòng đợi khoảng 1 phút rồi tiếp tục trò chuyện nhé!"
)

_SESSION_CHAT_LIMITER = BoundedSlidingWindowLimiter(max_keys=10_000)
_IP_CHAT_LIMITER = BoundedSlidingWindowLimiter(max_keys=10_000)
_CUSTOMER_SCORE_LIMITER = BoundedSlidingWindowLimiter(max_keys=10_000)


def _utcnow() -> datetime:
    """Naive UTC datetime để so sánh với giá trị DB."""
    return datetime.now(UTC).replace(tzinfo=None)


def _normalize_phone(raw: str) -> str:
    cleaned = re.sub(r"[\s.\-]", "", raw)
    return re.sub(r"^\+84", "0", cleaned)


def _extract_phone(text: str) -> str | None:
    match = PHONE_RE.search(text)
    return _normalize_phone(match.group(0)) if match else None


def _extract_name(text: str) -> str | None:
    match = NAME_RE.search(text)
    if not match:
        return None
    name = re.split(
        r"[,.;\n]|số điện thoại|sđt|phone", match.group(1), maxsplit=1, flags=re.IGNORECASE
    )[0]
    return name.strip()[:255] or None


def _rate_limited(session_id: str) -> bool:
    limit = get_settings().chat_rate_limit_per_minute
    return _SESSION_CHAT_LIMITER.is_limited(f"chat-session:{session_id}", limit)


def _client_rate_limited(request: Request) -> bool:
    limit = get_settings().chat_ip_rate_limit_per_minute
    return _IP_CHAT_LIMITER.is_limited(
        f"chat-ip:{client_identifier(request)}",
        limit,
    )


def _get_or_create_conversation(db: Session, session_id: str) -> Conversation:
    conversation = db.scalar(select(Conversation).where(Conversation.session_id == session_id))
    if conversation is None:
        conversation = Conversation(session_id=session_id)
        db.add(conversation)
        db.flush()
    return conversation


def _save_ai_message(
    db: Session, conversation: Conversation, content: str, meta: dict | None = None
) -> None:
    db.add(Message(conversation_id=conversation.id, role="ai", content=content, meta=meta))
    conversation.last_message_at = _utcnow()


def _match_fallback_rule(db: Session, text: str) -> FallbackRule | None:
    normalized = text.lower()
    rules = (
        db.query(FallbackRule)
        .filter(FallbackRule.is_active.is_(True))
        .order_by(FallbackRule.priority.desc(), FallbackRule.keyword.asc())
        .all()
    )
    for rule in rules:
        keyword = rule.keyword.strip().lower()
        if keyword and keyword in normalized:
            return rule
    return None


def _chat_summary_from_history(history: list[Message]) -> str:
    user_lines = [m.content.strip() for m in history if m.role == "user" and m.content.strip()]
    return "\n".join(user_lines[-8:])[:2000]


PURPOSE_TO_V2 = {"ở thật": "to_live", "đầu tư": "to_invest", "cho thuê": "to_invest"}

# Điểm rubric "Chủ động để lại SĐT sớm" (Mục 6.3)
PHONE_CAPTURE_SCORE_BONUS = 15


def _current_lead_score(db: Session, conversation: Conversation) -> int:
    """Điểm cộng dồn: ưu tiên hồ sơ khách; khách ẩn danh đọc từ meta tin AI cuối."""
    if conversation.customer_id:
        customer = db.get(Customer, conversation.customer_id)
        if customer is not None and customer.lead_score is not None:
            return customer.lead_score
    return anonymous_score_from_meta(db, conversation)


def _bump_capture_score(customer: Customer) -> None:
    score = min(100, (customer.lead_score or 0) + PHONE_CAPTURE_SCORE_BONUS)
    customer.lead_score = score
    customer.temperature = temperature_for(score)


def _apply_detected_to_customer(
    db: Session, customer: Customer, detected: DetectedProfile, result: dict
) -> None:
    if detected.customer_type != "unknown":
        customer.customer_type = detected.customer_type
    if detected.temperature != "unknown":
        customer.temperature = detected.temperature
    if detected.lead_score is not None:
        customer.lead_score = detected.lead_score
    if detected.unit_type and not customer.preferred_unit_type:
        customer.preferred_unit_type = detected.unit_type
    if detected.interested_subdivision and customer.interested_subdivision_id is None:
        subdivision_id = db.scalar(
            select(Subdivision.id).where(Subdivision.slug == detected.interested_subdivision)
        )
        if subdivision_id is not None:
            customer.interested_subdivision_id = subdivision_id
    profile = result.get("user_profile") or {}
    if customer.purpose == "unknown":
        mapped = PURPOSE_TO_V2.get(profile.get("purpose") or "")
        if mapped:
            customer.purpose = mapped
    if profile.get("budget") and customer.budget_max is None:
        customer.budget_max = profile["budget"]


def _response(
    *,
    session_id: str,
    text: str,
    analysis: str,
    status: str = "ok",
    require_lead_capture: bool = False,
    trigger_handover: bool = False,
    recommended_zones: list[ZoneMatch] | None = None,
    citations: list | None = None,
    detected: DetectedProfile | None = None,
) -> ChatResponse:
    return ChatResponse(
        status=status,
        reply=text,
        response=text,
        require_lead_capture=require_lead_capture,
        trigger_handover=trigger_handover,
        recommended_zones=recommended_zones or [],
        citations=citations or [],
        detected=detected,
        session_id=session_id,
        analysis=analysis,
    )


# ── POST /agent/chat ──────────────────────────────────────────────────────────


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat với AI Advisor",
    description=(
        "Gửi tin nhắn, nhận phản hồi từ AI Vinhomes Ocean Park Advisor. "
        "Sau FREE_MESSAGE_LIMIT tin của khách chưa để lại thông tin, API trả "
        "`require_lead_capture=true` — FE bung form 'Tạo đơn tư vấn' và khoá ô nhập "
        "cho tới khi khách submit POST /api/v1/customers/capture."
    ),
)
async def chat(
    request: ChatRequest,
    http_request: Request,
    db: Session = Depends(get_db),
) -> ChatResponse:
    settings = get_settings()
    session_id = request.session_id or str(uuid.uuid4())
    new_user_text = request.messages[-1].content

    try:
        if _rate_limited(session_id) or _client_rate_limited(http_request):
            return _response(
                session_id=session_id, text=RATE_LIMIT_MESSAGE, analysis="rate_limited"
            )

        conversation = _get_or_create_conversation(db, session_id)

        # Lưu tin nhắn khách (chống double-submit tin trùng liền kề).
        last_message = (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .first()
        )
        if not (last_message and last_message.role == "user" and last_message.content == new_user_text):
            db.add(Message(conversation_id=conversation.id, role="user", content=new_user_text))
            conversation.user_message_count += 1
            conversation.last_message_at = _utcnow()
            db.commit()

        # ── Gate: chặn sau FREE_MESSAGE_LIMIT tin nếu chưa capture ──────────
        if (
            not conversation.is_lead_captured
            and conversation.user_message_count > settings.free_message_limit
            and not _extract_phone(new_user_text)
        ):
            _save_ai_message(db, conversation, LEAD_CAPTURE_MESSAGE, {"gate": "lead_capture"})
            db.commit()
            return _response(
                session_id=session_id,
                text=LEAD_CAPTURE_MESSAGE,
                analysis="require_lead_capture",
                require_lead_capture=True,
            )

        # ── Khách để lại SĐT trong chat → capture ngay ───────────────────────
        captured_phone = _extract_phone(new_user_text)
        if captured_phone:
            history = (
                db.query(Message)
                .filter(Message.conversation_id == conversation.id)
                .order_by(Message.created_at.asc())
                .all()
            )
            customer = get_or_create_customer_by_phone(
                db, phone=captured_phone, full_name=_extract_name(new_user_text), source="chat"
            )
            if not customer.needs_summary:
                customer.needs_summary = _chat_summary_from_history(history)
            _bump_capture_score(customer)
            auto_assign_sale(db, customer)
            if customer.status == "new":
                customer.status = "contacted"
            conversation.customer_id = customer.id
            conversation.is_lead_captured = True
            response_text = (
                "Cảm ơn Anh/Chị, em đã ghi nhận thông tin liên hệ và chuyển cho Sales phụ trách. "
                "Chuyên viên sẽ liên hệ để xác nhận quỹ căn, giá chốt và phương án phù hợp nhất."
            )
            _save_ai_message(db, conversation, response_text, {"capture": "phone_in_chat"})
            db.commit()
            return _response(
                session_id=session_id,
                text=response_text,
                analysis="lead_captured",
                trigger_handover=True,
            )

        # ── Fallback rule (trả lời cứng theo keyword — cố ý, log rõ) ─────────
        fallback_rule = _match_fallback_rule(db, new_user_text)
        if fallback_rule is not None:
            logger.info(
                "[agent_routes] session=%s answer_path=fallback_rule keyword=%r",
                session_id,
                fallback_rule.keyword,
            )
            _save_ai_message(
                db, conversation, fallback_rule.response_message, {"fallback_rule": fallback_rule.keyword}
            )
            db.commit()
            return _response(
                session_id=session_id,
                text=fallback_rule.response_message,
                analysis=f"fallback_rule:{fallback_rule.keyword}",
            )

        # ── Chạy agent (chỉ truyền câu hỏi mới nhất; lịch sử cho profile) ────
        history = (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc())
            .all()
        )
        profile_messages = [
            {"role": "assistant" if m.role == "ai" else m.role, "content": m.content} for m in history
        ]
        result = await agent.ainvoke(
            {
                "messages": [{"role": "user", "content": new_user_text}],
                "profile_messages": profile_messages,
                "session_id": session_id,
                "current_lead_score": _current_lead_score(db, conversation),
            }
        )

        raw_zones = result.get("recommended_zones", [])
        recommended_zones = [
            ZoneMatch(
                name=z.get("name", ""),
                slug=z.get("slug", ""),
                match_reason=z.get("match_reason", ""),
                price_range=z.get("price_range", ""),
                design_style=z.get("design_style", ""),
            )
            for z in raw_zones
        ]

        detected_raw = result.get("detected") or {}
        detected_fields = {
            k: v
            for k, v in detected_raw.items()
            if k in DetectedProfile.model_fields
        }
        detected = DetectedProfile(**detected_fields) if detected_raw else None

        # Lead nóng cũng được coi là cần handover (Mục 6.4).
        trigger_handover = bool(
            result.get("trigger_handover", False)
            or (detected is not None and detected.temperature == "hot")
        )

        # Cập nhật hồ sơ khách nếu đã capture (profile_node chấm sau mỗi lượt).
        if conversation.customer_id and detected is not None:
            customer = db.get(Customer, conversation.customer_id)
            if customer is not None:
                _apply_detected_to_customer(db, customer, detected, result)
                if trigger_handover:
                    auto_assign_sale(db, customer)
                    if customer.status == "new":
                        customer.status = "contacted"

        meta = {
            "intent": result.get("intent", ""),
            "citations": [dict(c) for c in result.get("citations", [])][:5],
        }
        if detected_raw:
            meta["detected"] = detected_raw
        _save_ai_message(db, conversation, result.get("response", ""), meta)
        db.commit()

        return _response(
            session_id=session_id,
            text=result.get("response", ""),
            analysis=result.get("intent", ""),
            status=result.get("status", "ok"),
            trigger_handover=trigger_handover,
            recommended_zones=recommended_zones,
            citations=result.get("citations", []),
            detected=detected,
        )

    except Exception as e:
        db.rollback()
        logger.exception("Agent chat error for session %s", session_id)
        raise HTTPException(status_code=500, detail="Lỗi hệ thống. Vui lòng thử lại sau.") from e


# ── POST /agent/recommend ─────────────────────────────────────────────────────


@router.post(
    "/recommend",
    response_model=RecommendResponse,
    summary="Gợi ý phân khu phù hợp",
    description=(
        "Không cần chat context. Truyền trực tiếp budget / unit_type / purpose "
        "để nhận danh sách phân khu phù hợp nhất, kèm lý do và thông tin chi tiết."
    ),
)
async def recommend(request: RecommendRequest) -> RecommendResponse:
    try:
        raw = get_zone_recommendations(
            budget=request.budget,
            unit_type=request.unit_type,
            purpose=request.purpose,
            top_k=request.top_k,
        )
        zones = [RecommendZone(**z) for z in raw]
        return RecommendResponse(total=len(zones), recommendations=zones)
    except Exception as e:
        logger.exception("Zone recommend error")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống. Vui lòng thử lại sau.") from e


# ── POST /agent/customer-score ────────────────────────────────────────────────


@router.post(
    "/customer-score",
    response_model=CustomerScoreResponse,
    summary="Chấm điểm tiềm năng khách hàng",
    description=(
        "Dùng AI để phân loại khách thành HOT / WARM / COLD dựa trên "
        "lịch sử chat và profile. Endpoint này KHÔNG lưu vào database."
    ),
)
async def customer_score(
    request: CustomerScoreRequest,
    user: User = Depends(require_permission("customer.edit")),
) -> CustomerScoreResponse:
    settings = get_settings()
    if _CUSTOMER_SCORE_LIMITER.is_limited(
        f"customer-score-user:{user.id}",
        settings.customer_score_rate_limit_per_minute,
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Quá nhiều yêu cầu chấm điểm. Vui lòng thử lại sau.",
            headers={"Retry-After": "60"},
        )
    try:
        chat_history_dicts = [{"role": m.role, "content": m.content} for m in request.chat_history]
        user_profile_dict = request.user_profile.model_dump(exclude_none=False)

        scoring = await score_lead_detail(
            chat_history=chat_history_dicts,
            user_profile=user_profile_dict,
            name=request.name,
        )

        return CustomerScoreResponse(
            score=scoring["score"],  # type: ignore[arg-type]
            numeric_score=scoring["numeric_score"],
            score_reason=scoring["score_reason"],
            scoring_breakdown=scoring["breakdown"],
            handover_recommended=scoring["handover_recommended"],
            name=request.name,
            phone=request.phone,
        )
    except Exception as e:
        logger.exception("Customer scoring error for %s", request.name)
        raise HTTPException(status_code=500, detail="Lỗi hệ thống. Vui lòng thử lại sau.") from e


# ── GET /agent/status ─────────────────────────────────────────────────────────


@router.get(
    "/status",
    summary="Health-check agent",
    description="Kiểm tra trạng thái LangGraph agent và các features đang active.",
)
async def agent_status() -> dict:
    settings = get_settings()
    return {
        "status": "ready",
        "agent": "Vinhomes AI Advisor v2.0",
        "llm_provider": settings.llm_provider,
        "llm_configured": bool(settings.effective_llm_api_key),
        "llm_model": settings.effective_llm_model,
        "llm_base_url": settings.effective_llm_base_url,
        "free_message_limit": settings.free_message_limit,
        "endpoints": {
            "chat": "POST /agent/chat",
            "recommend": "POST /agent/recommend",
            "customer_score": "POST /agent/customer-score",
        },
        "features": [
            "intent-detection",
            "rag-zone-matching",
            "lead-capture-gating",
            "ai-customer-scoring",
        ],
    }
