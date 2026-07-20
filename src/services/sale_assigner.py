"""Tự phân công sale cho lead nóng (BAN_THIET_KE_V2 Mục 5.3).

Ưu tiên sale phụ trách phân khu khách quan tâm (user_subdivisions);
nếu nhiều ứng viên → chọn sale đang có ít khách được phân công nhất
(round-robin theo tải). Không có ai phụ trách phân khu → xét mọi sale active.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.entities import Customer, User, user_subdivisions


def auto_assign_sale(db: Session, customer: Customer) -> User | None:
    """Gán sale cho khách nếu chưa có; trả về sale được chọn (hoặc None)."""
    if customer.assigned_sale_id is not None:
        return db.get(User, customer.assigned_sale_id)

    candidates: list[User] = []
    if customer.interested_subdivision_id is not None:
        candidates = list(
            db.scalars(
                select(User)
                .join(user_subdivisions, user_subdivisions.c.user_id == User.id)
                .where(
                    user_subdivisions.c.subdivision_id == customer.interested_subdivision_id,
                    User.role == "sale",
                    User.is_active.is_(True),
                )
            ).all()
        )
    if not candidates:
        candidates = list(
            db.scalars(select(User).where(User.role == "sale", User.is_active.is_(True))).all()
        )
    if not candidates:
        return None

    def _load(sale: User) -> int:
        return db.scalar(
            select(func.count(Customer.id)).where(Customer.assigned_sale_id == sale.id)
        ) or 0

    chosen = min(candidates, key=lambda sale: (_load(sale), sale.id))
    customer.assigned_sale_id = chosen.id
    return chosen
