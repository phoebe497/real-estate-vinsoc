"""Auth/RBAC dependencies cho Sale/Admin (khách chat ẩn danh, không cần token).

- `get_current_user`: xác thực JWT của sale/admin.
- `require_roles`: kiểm tra role thô (admin | sale).
- `require_permission(code)`: admin mặc định có toàn quyền; sale cần được cấp
  quyền qua bảng user_permissions (menu Phân quyền).
"""

from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.entities import Permission, User, user_permissions
from src.services.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Phiên đăng nhập không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        if payload.get("type", "admin") != "admin":
            raise ValueError("not an admin token")
        user_id = int(payload.get("sub", ""))
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise credentials_error from None
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_error
    return user


def get_user_permission_codes(db: Session, user: User) -> set[str]:
    """Danh sách code quyền đã cấp cho user (admin trả về toàn bộ)."""
    if user.role == "admin":
        return set(db.scalars(select(Permission.code)).all())
    return set(
        db.scalars(
            select(Permission.code)
            .join(user_permissions, user_permissions.c.permission_id == Permission.id)
            .where(user_permissions.c.user_id == user.id)
        ).all()
    )


def user_has_permission(db: Session, user: User, code: str) -> bool:
    if user.role == "admin":
        return True
    return bool(
        db.scalar(
            select(Permission.id)
            .join(user_permissions, user_permissions.c.permission_id == Permission.id)
            .where(user_permissions.c.user_id == user.id, Permission.code == code)
        )
    )


def require_roles(*roles: str) -> Callable:
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không đủ quyền truy cập")
        return user

    return dependency


def require_permission(code: str) -> Callable:
    def dependency(
        user: User = Depends(get_current_user), db: Session = Depends(get_db)
    ) -> User:
        if not user_has_permission(db, user, code):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không đủ quyền truy cập")
        return user

    return dependency
