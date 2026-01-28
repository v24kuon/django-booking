from datetime import datetime, timezone

from sqlmodel import Session

from app.errors import AuthorizationError, ValidationError
from app.models import StallholderProfile, User
from app.repositories.profile_repo import get_stallholder_profile, save_stallholder_profile


def update_stallholder_profile(
    session: Session,
    user: User,
    business_name: str,
    genre: str,
    bio: str,
    website_url: str | None,
    past_achievements: str | None,
) -> StallholderProfile:
    if user.role != "stallholder":
        raise AuthorizationError("role_required_stallholder")

    profile = get_stallholder_profile(session, user.id)
    if not profile:
        raise ValidationError("profile_not_found")

    profile.business_name = business_name
    profile.genre = genre
    profile.bio = bio
    profile.website_url = website_url
    profile.past_achievements = past_achievements
    profile.updated_at = datetime.now(timezone.utc)
    return save_stallholder_profile(session, profile)
