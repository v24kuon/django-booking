from app.errors import AuthenticationError, ValidationError
from app.services.auth_service import authenticate_user, register_user


def test_register_user_creates_profile(session):
    # Given: valid registration data
    email = "stall@example.com"
    password = "password123"

    # When: registering a stallholder
    user = register_user(session, email=email, password=password, role="stallholder")

    # Then: user is created with profile
    assert user.id is not None
    assert user.email == email
    assert user.role == "stallholder"


def test_register_user_empty_email(session):
    # Given: empty email
    # When: registering
    try:
        register_user(session, email="", password="password123", role="stallholder")
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "email_required"
    else:
        raise AssertionError("ValidationError not raised")


def test_register_user_invalid_email(session):
    # Given: invalid email
    # When: registering
    try:
        register_user(session, email="invalid-email", password="password123", role="stallholder")
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "email_invalid"
    else:
        raise AssertionError("ValidationError not raised")


def test_register_user_short_password(session):
    # Given: password too short (min-1)
    # When: registering
    try:
        register_user(session, email="short@example.com", password="1234567", role="stallholder")
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "password_too_short"
    else:
        raise AssertionError("ValidationError not raised")


def test_register_user_duplicate_email(session):
    # Given: existing user
    register_user(session, email="dup@example.com", password="password123", role="stallholder")

    # When: registering with duplicate email
    try:
        register_user(session, email="dup@example.com", password="password123", role="stallholder")
    except ValidationError as exc:
        # Then: duplicate email error
        assert str(exc) == "email_exists"
    else:
        raise AssertionError("ValidationError not raised")


def test_authenticate_user_success(session):
    # Given: registered user
    register_user(session, email="login@example.com", password="password123", role="stallholder")

    # When: login with correct credentials
    user = authenticate_user(session, email="login@example.com", password="password123")

    # Then: authenticated user returned
    assert user.email == "login@example.com"


def test_authenticate_user_wrong_password(session):
    # Given: registered user
    register_user(session, email="wrong@example.com", password="password123", role="stallholder")

    # When: login with wrong password
    try:
        authenticate_user(session, email="wrong@example.com", password="badpassword")
    except AuthenticationError as exc:
        # Then: authentication error
        assert str(exc) == "invalid_credentials"
    else:
        raise AssertionError("AuthenticationError not raised")


def test_authenticate_user_inactive(session):
    # Given: inactive user
    user = register_user(session, email="inactive@example.com", password="password123", role="stallholder")
    user.is_active = False
    session.add(user)
    session.commit()

    # When: login with inactive account
    try:
        authenticate_user(session, email="inactive@example.com", password="password123")
    except AuthenticationError as exc:
        # Then: authentication blocked
        assert str(exc) == "inactive_account"
    else:
        raise AssertionError("AuthenticationError not raised")


def test_register_user_null_email(session):
    # Given: null email
    # When: registering
    try:
        register_user(session, email=None, password="password123", role="stallholder")
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "email_required"
    else:
        raise AssertionError("ValidationError not raised")


def test_register_user_admin_not_allowed(session):
    # Given: admin role registration attempt
    # When: registering without allow_admin
    try:
        register_user(session, email="admin@example.com", password="password123", role="admin")
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "admin_registration_not_allowed"
    else:
        raise AssertionError("ValidationError not raised")


def test_register_user_long_password(session):
    # Given: password too long (max+1)
    # When: registering
    long_password = "a" * 73
    try:
        register_user(session, email="long@example.com", password=long_password, role="stallholder")
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "password_too_long"
    else:
        raise AssertionError("ValidationError not raised")
