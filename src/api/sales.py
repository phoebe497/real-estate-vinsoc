"""Sales management API — menu 'Quản lý Sale' và 'Phân quyền' (Mục 8, 10).

Cần quyền `sales.manage` (admin mặc định có). Riêng phân quyền cần
`permissions.manage`.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from src.api.dependencies import require_permission
from src.db.session import get_db
from src.models.entities import (
    Customer,
    Permission,
    PurchaseHistory,
    SaleAward,
    Subdivision,
    User,
    user_permissions,
)
from src.models.schemas import (
    PermissionResponse,
    SaleAwardCreateRequest,
    SaleAwardResponse,
    SaleCreateRequest,
    SaleResponse,
    SaleSubdivisionsUpdateRequest,
    SaleUpdateRequest,
    UserPermissionsUpdateRequest,
)
from src.services.security import hash_password

router = APIRouter(tags=["sales-management"])


def _sale_response(db: Session, user: User) -> SaleResponse:
    assigned_count = db.scalar(
        select(func.count(Customer.id)).where(Customer.assigned_sale_id == user.id)
    ) or 0
    sold_count = db.scalar(
        select(func.count(PurchaseHistory.id)).where(PurchaseHistory.responsible_sale_id == user.id)
    ) or 0
    response = SaleResponse.model_validate(user)
    response.assigned_customer_count = assigned_count
    response.sold_count = sold_count
    return response


def _get_sale(db: Session, sale_id: int) -> User:
    user = db.scalar(
        select(User)
        .where(User.id == sale_id)
        .options(selectinload(User.subdivisions), selectinload(User.awards))
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản sale")
    return user


# ── CRUD sale ────────────────────────────────────────────────────────────────


@router.get("/sales", response_model=list[SaleResponse])
def list_sales(
    _: User = Depends(require_permission("sales.manage")), db: Session = Depends(get_db)
) -> list[SaleResponse]:
    users = db.scalars(
        select(User)
        .options(selectinload(User.subdivisions), selectinload(User.awards))
        .order_by(User.full_name)
    ).all()
    return [_sale_response(db, user) for user in users]


@router.post("/sales", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(
    request: SaleCreateRequest,
    _: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db),
) -> SaleResponse:
    email = str(request.email).lower()
    if db.scalar(select(User.id).where(User.email == email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email đã tồn tại")
    user = User(
        email=email,
        full_name=request.full_name,
        password_hash=hash_password(request.password),
        role=request.role,
        phone=request.phone,
        title=request.title,
        avatar_url=request.avatar_url,
        work_shift_start=request.work_shift_start,
        work_shift_end=request.work_shift_end,
        join_date=request.join_date,
    )
    db.add(user)
    db.commit()
    return _sale_response(db, _get_sale(db, user.id))


@router.get("/sales/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    _: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db),
) -> SaleResponse:
    return _sale_response(db, _get_sale(db, sale_id))


@router.patch("/sales/{sale_id}", response_model=SaleResponse)
def update_sale(
    sale_id: int,
    request: SaleUpdateRequest,
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db),
) -> SaleResponse:
    user = _get_sale(db, sale_id)
    updates = request.model_dump(exclude_unset=True)
    if updates.get("is_active") is False and user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Không thể tự khóa tài khoản hiện tại"
        )
    if "password" in updates:
        user.password_hash = hash_password(updates.pop("password"))
    for field, value in updates.items():
        setattr(user, field, value)
    db.commit()
    return _sale_response(db, _get_sale(db, sale_id))


@router.delete("/sales/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(
    sale_id: int,
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db),
) -> None:
    user = _get_sale(db, sale_id)
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Không thể tự xóa tài khoản hiện tại"
        )
    # Khách đã phân công cho sale này chuyển về chưa phân công (FK SET NULL).
    db.delete(user)
    db.commit()


# ── Giải thưởng ──────────────────────────────────────────────────────────────


@router.get("/sales/{sale_id}/awards", response_model=list[SaleAwardResponse])
def list_awards(
    sale_id: int,
    _: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db),
) -> list[SaleAward]:
    _get_sale(db, sale_id)
    return list(
        db.scalars(
            select(SaleAward).where(SaleAward.user_id == sale_id).order_by(SaleAward.awarded_at.desc())
        ).all()
    )


@router.post(
    "/sales/{sale_id}/awards", response_model=SaleAwardResponse, status_code=status.HTTP_201_CREATED
)
def create_award(
    sale_id: int,
    request: SaleAwardCreateRequest,
    _: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db),
) -> SaleAward:
    _get_sale(db, sale_id)
    award = SaleAward(user_id=sale_id, **request.model_dump())
    db.add(award)
    db.commit()
    db.refresh(award)
    return award


@router.delete("/sales/{sale_id}/awards/{award_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_award(
    sale_id: int,
    award_id: int,
    _: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db),
) -> None:
    award = db.scalar(select(SaleAward).where(SaleAward.id == award_id, SaleAward.user_id == sale_id))
    if award is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy giải thưởng")
    db.delete(award)
    db.commit()


# ── Phân khu phụ trách ───────────────────────────────────────────────────────


@router.put("/sales/{sale_id}/subdivisions", response_model=SaleResponse)
def set_sale_subdivisions(
    sale_id: int,
    request: SaleSubdivisionsUpdateRequest,
    _: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db),
) -> SaleResponse:
    user = _get_sale(db, sale_id)
    subdivisions = list(
        db.scalars(select(Subdivision).where(Subdivision.id.in_(request.subdivision_ids))).all()
    )
    if len(subdivisions) != len(set(request.subdivision_ids)):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Phân khu không hợp lệ")
    user.subdivisions = subdivisions
    db.commit()
    return _sale_response(db, _get_sale(db, sale_id))


# ── Phân quyền ───────────────────────────────────────────────────────────────


@router.get("/permissions", response_model=list[PermissionResponse])
def list_permissions(
    _: User = Depends(require_permission("permissions.manage")), db: Session = Depends(get_db)
) -> list[Permission]:
    return list(db.scalars(select(Permission).order_by(Permission.group_name, Permission.code)).all())


@router.get("/sales/{sale_id}/permissions", response_model=list[PermissionResponse])
def get_sale_permissions(
    sale_id: int,
    _: User = Depends(require_permission("permissions.manage")),
    db: Session = Depends(get_db),
) -> list[Permission]:
    user = _get_sale(db, sale_id)
    if user.role == "admin":
        return list(db.scalars(select(Permission).order_by(Permission.group_name, Permission.code)).all())
    return list(
        db.scalars(
            select(Permission)
            .join(user_permissions, user_permissions.c.permission_id == Permission.id)
            .where(user_permissions.c.user_id == sale_id)
            .order_by(Permission.group_name, Permission.code)
        ).all()
    )


@router.put("/sales/{sale_id}/permissions", response_model=list[PermissionResponse])
def set_sale_permissions(
    sale_id: int,
    request: UserPermissionsUpdateRequest,
    _: User = Depends(require_permission("permissions.manage")),
    db: Session = Depends(get_db),
) -> list[Permission]:
    """Ghi đè danh sách quyền được tick cho một sale (admin không cần cấp)."""
    user = _get_sale(db, sale_id)
    if user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Admin mặc định có toàn quyền"
        )
    permissions = list(db.scalars(select(Permission).where(Permission.code.in_(request.codes))).all())
    if len(permissions) != len(set(request.codes)):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Mã quyền không hợp lệ")
    db.execute(delete(user_permissions).where(user_permissions.c.user_id == sale_id))
    for permission in permissions:
        db.execute(user_permissions.insert().values(user_id=sale_id, permission_id=permission.id))
    db.commit()
    return sorted(permissions, key=lambda p: (p.group_name, p.code))
