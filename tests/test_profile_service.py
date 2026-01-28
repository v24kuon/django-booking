from app.errors import AuthorizationError
from app.services.auth_service import register_user
from app.services.profile_service import update_stallholder_profile


def test_update_stallholder_profile_success(session):
    # Given: stallholder user
    user = register_user(session, "stallprofile@example.com", "password123", "stallholder")

    # When: updating profile
    profile = update_stallholder_profile(
        session,
        user,
        business_name="Sun Cafe",
        genre="food",
        bio="Hello",
        website_url="https://example.com",
        past_achievements="Award",
    )

    # Then: profile updated
    assert profile.business_name == "Sun Cafe"
    assert profile.website_url == "https://example.com"


def test_update_stallholder_profile_wrong_role(session):
    # Given: organizer user
    user = register_user(session, "orgprofile@example.com", "password123", "organizer")

    # When: updating as organizer
    try:
        update_stallholder_profile(
            session,
            user,
            business_name="Sun Cafe",
            genre="food",
            bio="Hello",
            website_url="https://example.com",
            past_achievements="Award",
        )
    except AuthorizationError as exc:
        # Then: authorization error
        assert str(exc) == "role_required_stallholder"
    else:
        raise AssertionError("AuthorizationError not raised")
