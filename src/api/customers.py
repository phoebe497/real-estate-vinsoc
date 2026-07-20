"""Customers API — thực thể trung tâm của CRM (BAN_THIET_KE_V2 Mục 8).

Public:
  POST /customers/capture  — thu thập tên + SĐT từ form trong chat/liên hệ.
  POST /contact            — form liên hệ trang public (tương thích FE cũ).

CRM (JWT):
  GET   /customers                       — sale thấy khách được phân công;
                                           admin/`customer.view_all` thấy tất cả.
  GET   /customers/{id}
  PATCH /customers/{id}                  — cần `customer.edit`.
  POST  /customers/{id}/assign           — cần `customer.assign`.
  GET   /customers/{id}/conversations    — cần `customer.view_chat`.
  POST  /customers/{id}/notes
  GET/POST /customers/{id}/purchases
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from src.api.dependencies import get_current_user, require_permission, user_has_permission
from src.db.session import get_db
from src.models.entities import (
    Conversation,
    Customer,
    CustomerNote,
    Message,
    PurchaseHistory,
    Subdivision,
    User,
)
from src.models.schemas import (
    ContactRequest,
    ConversationDetailResponse,
    ConversationSummaryResponse,
    CustomerAssignRequest,
    CustomerCaptureRequest,
    CustomerCaptureResponse,
    CustomerDetailResponse,
    CustomerNoteCreateRequest,
    CustomerNoteResponse,
    CustomerResponse,
    CustomerUpdateRequest,
    PurchaseCreateRequest,
    PurchaseResponse,
)

router = APIRouter(tags=["customers"])


def _normalize_phone(raw: str) -> str:
    cleaned = re.sub(r"[\s\-\.]", "", raw)
    return re.sub(r"^\+84", "0", cleaned)


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def get_or_create_customer_by_phone(
    db: Session,
    *,
    phone: str,
    full_name: str | None = None,
    source: str = "chat",
) -> Customer:
    """Tìm/tạo Customer theo phone — điểm vào duy nhất để tránh trùng khách."""
    phone = _normalize_phone(phone)
    customer = db.scalar(select(Customer).where(Customer.phone == phone))
    if customer is None:
        customer = Customer(full_name=full_name, phone=phone, source=source)
        db.add(customer)
        db.flush()
    elif full_name and not customer.full_name:
        customer.full_name = full_name
    return customer


def anonymous_score_from_meta(db: Session, conversation: Conversation) -> int:
    """Điểm lead tích lũy khi khách còn ẩn danh, đọc từ meta tin AI gần nhất."""
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id, Message.role == "ai")
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(10)
        .all()
    )
    for message in messages:
        detected = (message.meta or {}).get("detected") or {}
        if detected.get("lead_score") is not None:
            return int(detected["lead_score"])
    return 0


def link_conversation_to_customer(
    db: Session, session_id: str | None, customer: Customer
) -> tuple[Conversation | None, bool]:
    """Gán conversation cho khách; trả về (conversation, có phải capture lần đầu)."""
    if not session_id:
        return None, False
    conversation = db.scalar(select(Conversation).where(Conversation.session_id == session_id))
    if conversation is None:
        return None, False
    newly_captured = not conversation.is_lead_captured
    conversation.customer_id = customer.id
    conversation.is_lead_captured = True
    return conversation, newly_captured


# ── Public endpoints ─────────────────────────────────────────────────────────


@router.post(
    "/customers/capture",
    response_model=CustomerCaptureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thu thập thông tin khách (lead capture)",
)
def capture_customer(request: CustomerCaptureRequest, db: Session = Depends(get_db)) -> CustomerCaptureResponse:
    """Form 'Tạo đơn tư vấn' trong chat widget hoặc khi bị chặn sau 3 tin.

    Tạo/tìm Customer theo phone, gán vào conversation (nếu có session_id)
    và mở khóa chat (`is_lead_captured=true`).
    """
    customer = get_or_create_customer_by_phone(
        db, phone=request.phone, full_name=request.full_name, source="contact_form"
    )
    if request.email:
        customer.email = str(request.email)
    if request.preferred_unit_type:
        customer.preferred_unit_type = request.preferred_unit_type
    if request.budget_min is not None:
        customer.budget_min = request.budget_min
    if request.budget_max is not None:
        customer.budget_max = request.budget_max
    if request.purpose != "unknown":
        customer.purpose = request.purpose
    customer.consent_contact = request.consent_contact
    if request.interested_subdivision_slug:
        subdivision_id = db.scalar(
            select(Subdivision.id).where(Subdivision.slug == request.interested_subdivision_slug)
        )
        if subdivision_id is not None:
            customer.interested_subdivision_id = subdivision_id
    note_parts = [part for part in (request.note, request.contact_time and f"Thời gian tiện liên hệ: {request.contact_time}") if part]
    if note_parts and not customer.needs_summary:
        customer.needs_summary = ". ".join(note_parts)

    conversation, newly_captured = link_conversation_to_customer(db, request.session_id, customer)
    if newly_captured and conversation is not None:
        # Kế thừa điểm tích lũy khi còn ẩn danh + rubric "để lại SĐT sớm" +15
        from src.agents.nodes.profile_node import temperature_for

        base = max(customer.lead_score or 0, anonymous_score_from_meta(db, conversation))
        score = min(100, base + 15)
        customer.lead_score = score
        customer.temperature = temperature_for(score)
    db.commit()
    return CustomerCaptureResponse(customer_id=customer.id)


@router.post(
    "/contact",
    response_model=CustomerCaptureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Form liên hệ trang public",
)
def submit_contact(request: ContactRequest, db: Session = Depends(get_db)) -> CustomerCaptureResponse:
    customer = get_or_create_customer_by_phone(
        db, phone=request.phone, full_name=request.name, source="contact_form"
    )
    if request.email:
        customer.email = str(request.email)
    if request.preferred_bedrooms:
        customer.preferred_unit_type = request.preferred_bedrooms
    if request.subdivision_slug:
        subdivision_id = db.scalar(
            select(Subdivision.id).where(Subdivision.slug == request.subdivision_slug)
        )
        if subdivision_id is not None:
            customer.interested_subdivision_id = subdivision_id
    if request.message and not customer.needs_summary:
        customer.needs_summary = request.message
    customer.consent_contact = True
    db.commit()
    return CustomerCaptureResponse(customer_id=customer.id)


# ── CRM endpoints ────────────────────────────────────────────────────────────


def _customer_scope(query, db: Session, user: User):
    """Sale chỉ thấy khách được phân công, trừ khi có `customer.view_all`."""
    if user_has_permission(db, user, "customer.view_all"):
        return query
    return query.where(Customer.assigned_sale_id == user.id)


def _get_visible_customer(customer_id: int, db: Session, user: User) -> Customer:
    customer = db.scalar(
        select(Customer)
        .where(Customer.id == customer_id)
        .options(
            selectinload(Customer.assigned_sale),
            selectinload(Customer.interested_subdivision),
            selectinload(Customer.notes).selectinload(CustomerNote.author),
            selectinload(Customer.purchases).selectinload(PurchaseHistory.subdivision),
            selectinload(Customer.purchases).selectinload(PurchaseHistory.responsible_sale),
        )
    )
    if customer is None or (
        not user_has_permission(db, user, "customer.view_all")
        and customer.assigned_sale_id != user.id
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy khách hàng")
    return customer


@router.get("/customers", response_model=list[CustomerResponse])
def list_customers(
    customer_status: str | None = Query(default=None, alias="status"),
    customer_type: str | None = None,
    temperature: str | None = None,
    search: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Customer]:
    query = select(Customer).options(
        selectinload(Customer.assigned_sale), selectinload(Customer.interested_subdivision)
    )
    query = _customer_scope(query, db, user)
    if customer_status:
        query = query.where(Customer.status == customer_status)
    if customer_type:
        query = query.where(Customer.customer_type == customer_type)
    if temperature:
        query = query.where(Customer.temperature == temperature)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(
            or_(Customer.full_name.ilike(pattern), Customer.phone.ilike(pattern), Customer.email.ilike(pattern))
        )
    return list(db.scalars(query.order_by(Customer.created_at.desc()).offset(offset).limit(limit)).all())


@router.get("/customers/{customer_id}", response_model=CustomerDetailResponse)
def get_customer(
    customer_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Customer:
    return _get_visible_customer(customer_id, db, user)


@router.patch("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    request: CustomerUpdateRequest,
    user: User = Depends(require_permission("customer.edit")),
    db: Session = Depends(get_db),
) -> Customer:
    customer = _get_visible_customer(customer_id, db, user)
    updates = request.model_dump(exclude_unset=True)
    if "interested_subdivision_id" in updates and updates["interested_subdivision_id"] is not None:
        if db.get(Subdivision, updates["interested_subdivision_id"]) is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Phân khu không hợp lệ")
    for field, value in updates.items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


@router.post("/customers/{customer_id}/assign", response_model=CustomerResponse)
def assign_customer(
    customer_id: int,
    request: CustomerAssignRequest,
    user: User = Depends(require_permission("customer.assign")),
    db: Session = Depends(get_db),
) -> Customer:
    customer = _get_visible_customer(customer_id, db, user)
    if request.sale_id is not None:
        sale = db.get(User, request.sale_id)
        if sale is None or not sale.is_active:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Sale không hợp lệ")
    customer.assigned_sale_id = request.sale_id
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/customers/{customer_id}/conversations", response_model=list[ConversationSummaryResponse])
def list_customer_conversations(
    customer_id: int,
    user: User = Depends(require_permission("customer.view_chat")),
    db: Session = Depends(get_db),
) -> list[Conversation]:
    customer = _get_visible_customer(customer_id, db, user)
    return list(
        db.scalars(
            select(Conversation)
            .where(Conversation.customer_id == customer.id)
            .order_by(Conversation.last_message_at.desc())
        ).all()
    )


@router.get(
    "/customers/{customer_id}/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
)
def get_customer_conversation(
    customer_id: int,
    conversation_id: int,
    user: User = Depends(require_permission("customer.view_chat")),
    db: Session = Depends(get_db),
) -> Conversation:
    customer = _get_visible_customer(customer_id, db, user)
    conversation = db.scalar(
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.customer_id == customer.id)
        .options(selectinload(Conversation.messages))
    )
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phiên chat")
    return conversation


@router.post(
    "/customers/{customer_id}/notes",
    response_model=CustomerNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_note(
    customer_id: int,
    request: CustomerNoteCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CustomerNote:
    customer = _get_visible_customer(customer_id, db, user)
    note = CustomerNote(customer_id=customer.id, author_id=user.id, content=request.content.strip())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/customers/{customer_id}/purchases", response_model=list[PurchaseResponse])
def list_customer_purchases(
    customer_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[PurchaseHistory]:
    customer = _get_visible_customer(customer_id, db, user)
    return list(
        db.scalars(
            select(PurchaseHistory)
            .where(PurchaseHistory.customer_id == customer.id)
            .options(
                selectinload(PurchaseHistory.subdivision),
                selectinload(PurchaseHistory.responsible_sale),
            )
            .order_by(PurchaseHistory.purchase_date.desc())
        ).all()
    )


@router.post(
    "/customers/{customer_id}/purchases",
    response_model=PurchaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_purchase(
    customer_id: int,
    request: PurchaseCreateRequest,
    user: User = Depends(require_permission("customer.edit")),
    db: Session = Depends(get_db),
) -> PurchaseHistory:
    customer = _get_visible_customer(customer_id, db, user)
    if db.get(Subdivision, request.subdivision_id) is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Phân khu không hợp lệ")
    if request.responsible_sale_id is not None and db.get(User, request.responsible_sale_id) is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Sale không hợp lệ")
    purchase = PurchaseHistory(customer_id=customer.id, **request.model_dump())
    db.add(purchase)
    db.commit()
    purchase = db.scalar(
        select(PurchaseHistory)
        .where(PurchaseHistory.id == purchase.id)
        .options(
            selectinload(PurchaseHistory.subdivision),
            selectinload(PurchaseHistory.responsible_sale),
        )
    )
    # Khách có giao dịch → cập nhật trạng thái pipeline nếu đang ở giai đoạn sớm
    if customer.status in ("new", "contacted", "consulting", "visiting"):
        customer.status = "won"
        db.commit()
    return purchase
