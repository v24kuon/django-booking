from datetime import datetime, timezone

from sqlmodel import Session

from app.errors import AuthenticationError, ValidationError
from app.models import OrganizerProfile, StallholderProfile, User
from app.repositories.profile_repo import (
    save_organizer_profile,
    save_stallholder_profile,
)
from app.repositories.user_repo import get_user_by_email, save_user
from app.security import hash_password, verify_password

ALLOWED_ROLES = {"stallholder", "organizer", "admin"}


def register_user(
    session: Session, email: str | None, password: str, role: str, allow_admin: bool = False
) -> User:
    if not email:
        raise ValidationError("email_required")
    if "@" not in email:
        raise ValidationError("email_invalid")
    if len(password) < 8:
        raise ValidationError("password_too_short")
    if len(password.encode("utf-8")) > 72:
        raise ValidationError("password_too_long")
    if role not in ALLOWED_ROLES:
        raise ValidationError("role_invalid")
    if role == "admin" and not allow_admin:
        raise ValidationError("admin_registration_not_allowed")

    existing = get_user_by_email(session, email)
    if existing:
        raise ValidationError("email_exists")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        role=role,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user = save_user(session, user)

    if role == "stallholder":
        profile = StallholderProfile(
            user_id=user.id,
            business_name="未設定",
            genre="未設定",
            bio="",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        save_stallholder_profile(session, profile)
    elif role == "organizer":
        profile = OrganizerProfile(
            user_id=user.id,
            organization_name="未設定",
            description="",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        save_organizer_profile(session, profile)

    return user


def authenticate_user(session: Session, email: str, password: str) -> User:
    user = get_user_by_email(session, email)
    if not user or not verify_password(password, user.hashed_password):
        raise AuthenticationError("invalid_credentials")
    if not user.is_active:
        raise AuthenticationError("inactive_account")

    user.last_login_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    save_user(session, user)
    return user
