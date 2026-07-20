from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user, get_user_permission_codes
from src.config import get_settings
from src.db.session import get_db
from src.models.entities import User
from src.models.schemas import (
    LoginRequest,
    MeResponse,
    ProfileUpdateRequest,
    TokenResponse,
    UserResponse,
)
from src.services.rate_limiter import BoundedSlidingWindowLimiter, client_identifier
from src.services.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["authentication"])
_LOGIN_IP_LIMITER = BoundedSlidingWindowLimiter(max_keys=10_000)
_LOGIN_ACCOUNT_LIMITER = BoundedSlidingWindowLimiter(max_keys=10_000)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    settings = get_settings()
    email = str(payload.email).lower()
    client_id = client_identifier(request)
    rate_limited = _LOGIN_IP_LIMITER.is_limited(
        f"login-ip:{client_id}",
        settings.login_ip_rate_limit_per_minute,
    )
    rate_limited = _LOGIN_ACCOUNT_LIMITER.is_limited(
        f"login-account:{email}",
        settings.login_account_rate_limit_per_minute,
    ) or rate_limited
    if rate_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Quá nhiều lần đăng nhập. Vui lòng thử lại sau.",
            headers={"Retry-After": "60"},
        )

    user = db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email hoặc mật khẩu không đúng")
    return TokenResponse(access_token=create_access_token(user.id, user.role), user=user)


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MeResponse:
    """Thông tin + danh sách quyền của tài khoản đang đăng nhập.

    FE dùng `permissions` để ẩn/hiện menu. Admin trả về toàn bộ quyền.
    """
    return MeResponse(
        user=UserResponse.model_validate(user),
        permissions=sorted(get_user_permission_codes(db, user)),
    )


@router.patch("/me", response_model=UserResponse)
def update_me(
    request: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Sale/Admin tự sửa profile cá nhân (không đổi được role/quyền)."""
    if request.full_name is not None:
        user.full_name = request.full_name
    if request.phone is not None:
        user.phone = request.phone
    if request.avatar_url is not None:
        user.avatar_url = request.avatar_url
    if request.title is not None:
        user.title = request.title
    if request.password is not None:
        user.password_hash = hash_password(request.password)
    db.commit()
    db.refresh(user)
    return user
