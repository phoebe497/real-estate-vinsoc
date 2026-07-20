"""Dashboard thống kê (BAN_THIET_KE_V2 Mục 11). Cần quyền `dashboard.view`."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.api.dependencies import require_permission, user_has_permission
from src.db.session import get_db
from src.models.entities import (
    Conversation,
    Customer,
    FallbackRule,
    Message,
    PurchaseHistory,
    Subdivision,
    User,
)
from src.models.schemas import (
    BreakdownItem,
    DashboardStatsResponse,
    SalePerformanceItem,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _breakdown(rows) -> list[BreakdownItem]:
    return [BreakdownItem(label=str(label or "unknown"), count=count) for label, count in rows]


@router.get("/stats", response_model=DashboardStatsResponse)
def dashboard_stats(
    days: int = 30,
    user: User = Depends(require_permission("dashboard.view")),
    db: Session = Depends(get_db),
) -> DashboardStatsResponse:
    now = _utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = today_start.replace(day=1)
    trend_start = today_start - timedelta(days=max(1, min(days, 365)) - 1)

    scoped = select(Customer)
    if not user_has_permission(db, user, "customer.view_all"):
        scoped = scoped.where(Customer.assigned_sale_id == user.id)
    customers = list(db.scalars(scoped).all())

    def _count_since(start: datetime) -> int:
        return sum(1 for c in customers if c.created_at and c.created_at.replace(tzinfo=None) >= start)

    type_counts: dict[str, int] = {}
    temp_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    trend_counts: dict[str, int] = {}
    for customer in customers:
        type_counts[customer.customer_type] = type_counts.get(customer.customer_type, 0) + 1
        temp_counts[customer.temperature] = temp_counts.get(customer.temperature, 0) + 1
        status_counts[customer.status] = status_counts.get(customer.status, 0) + 1
        created = customer.created_at.replace(tzinfo=None) if customer.created_at else None
        if created and created >= trend_start:
            key = created.strftime("%Y-%m-%d")
            trend_counts[key] = trend_counts.get(key, 0) + 1

    status_order = ["new", "contacted", "consulting", "visiting", "won", "lost"]
    status_funnel = [
        BreakdownItem(label=st, count=status_counts.get(st, 0)) for st in status_order
    ]

    conversation_count = db.scalar(select(func.count(Conversation.id))) or 0
    captured_count = db.scalar(
        select(func.count(Conversation.id)).where(Conversation.is_lead_captured.is_(True))
    ) or 0
    message_count = db.scalar(select(func.count(Message.id))) or 0

    top_subdivision_rows = db.execute(
        select(Subdivision.name, func.count(Customer.id))
        .join(Customer, Customer.interested_subdivision_id == Subdivision.id)
        .group_by(Subdivision.name)
        .order_by(func.count(Customer.id).desc())
        .limit(5)
    ).all()

    sales_rows = db.scalars(select(User).where(User.role == "sale", User.is_active.is_(True))).all()
    sales_performance = []
    for sale in sales_rows:
        assigned = db.scalar(
            select(func.count(Customer.id)).where(Customer.assigned_sale_id == sale.id)
        ) or 0
        sold = db.scalar(
            select(func.count(PurchaseHistory.id)).where(PurchaseHistory.responsible_sale_id == sale.id)
        ) or 0
        sales_performance.append(
            SalePerformanceItem(id=sale.id, name=sale.full_name, assigned_count=assigned, sold_count=sold)
        )
    sales_performance.sort(key=lambda item: (item.sold_count, item.assigned_count), reverse=True)

    return DashboardStatsResponse(
        total_customers=len(customers),
        new_today=_count_since(today_start),
        new_this_week=_count_since(week_start),
        new_this_month=_count_since(month_start),
        conversations=conversation_count,
        messages=message_count,
        captured_conversations=captured_count,
        capture_rate=round(captured_count / conversation_count, 4) if conversation_count else 0.0,
        handover_customers=temp_counts.get("hot", 0),
        active_fallback_rules=db.scalar(
            select(func.count(FallbackRule.id)).where(FallbackRule.is_active.is_(True))
        ) or 0,
        customer_type_breakdown=_breakdown(sorted(type_counts.items(), key=lambda x: -x[1])),
        temperature_breakdown=_breakdown(sorted(temp_counts.items(), key=lambda x: -x[1])),
        status_funnel=status_funnel,
        top_subdivisions=_breakdown(top_subdivision_rows),
        customer_trend=[
            BreakdownItem(label=key, count=trend_counts[key]) for key in sorted(trend_counts)
        ],
        sales_performance=sales_performance[:10],
    )
