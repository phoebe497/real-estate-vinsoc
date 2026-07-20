from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config import Settings
from src.models.entities import User
from src.services.security import hash_password


def seed_admin(session: Session, settings: Settings) -> bool:
    email = settings.admin_email.strip().lower()
    if not email or not settings.admin_password:
        return False
    if session.scalar(select(User.id).where(User.email == email)):
        return False
    session.add(
        User(
            email=email,
            full_name=settings.admin_full_name,
            password_hash=hash_password(settings.admin_password),
            role="admin",
            is_active=True,
        )
    )
    session.commit()
    return True
