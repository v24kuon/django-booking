from datetime import datetime, timedelta, timezone

from app.errors import AuthorizationError, ValidationError
from sqlmodel import select

from app.models import Notification, User
from app.services.application_service import apply_to_event, cancel_application, decide_application
from app.services.auth_service import register_user
from app.services.event_service import create_event


def _create_open_event(session, organizer_email: str):
    organizer = register_user(session, organizer_email, "password123", "organizer")
    now = datetime.now(timezone.utc)
    event = create_event(
        session,
        organizer,
        title="Open Event",
        description="Sample event",
        region="Tokyo",
        venue_address="Shibuya",
        genre="food",
        start_date=now + timedelta(days=7),
        end_date=now + timedelta(days=8),
        application_deadline=now + timedelta(days=5),
        capacity=10,
    )
    event.status = "open"
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def test_apply_to_event_success(session):
    # Given: open event and stallholder
    event = _create_open_event(session, "org@app.com")
    stallholder = register_user(session, "stall@app.com", "password123", "stallholder")

    # When: applying to event
    application = apply_to_event(session, event, stallholder, memo="I want to join")

    # Then: application created
    assert application.id is not None
    assert application.status == "pending"
    notif = session.exec(
        select(Notification).where(Notification.user_id == event.organizer_id)
    ).first()
    assert notif is not None
    assert notif.event_type == "application_submitted"


def test_apply_to_event_not_open(session):
    # Given: draft event and stallholder
    organizer = register_user(session, "org2@app.com", "password123", "organizer")
    now = datetime.now(timezone.utc)
    event = create_event(
        session,
        organizer,
        title="Draft Event",
        description="Sample",
        region="Tokyo",
        venue_address="Shibuya",
        genre="food",
        start_date=now + timedelta(days=7),
        end_date=now + timedelta(days=8),
        application_deadline=now + timedelta(days=5),
        capacity=10,
    )
    stallholder = register_user(session, "stall2@app.com", "password123", "stallholder")

    # When: applying to non-open event
    try:
        apply_to_event(session, event, stallholder, memo="Apply")
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "event_not_open"
    else:
        raise AssertionError("ValidationError not raised")


def test_apply_to_event_duplicate(session):
    # Given: open event and stallholder
    event = _create_open_event(session, "org3@app.com")
    stallholder = register_user(session, "stall3@app.com", "password123", "stallholder")
    apply_to_event(session, event, stallholder, memo="First")

    # When: applying twice
    try:
        apply_to_event(session, event, stallholder, memo="Second")
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "application_exists"
    else:
        raise AssertionError("ValidationError not raised")


def test_apply_to_event_wrong_role(session):
    # Given: open event and organizer user
    event = _create_open_event(session, "org4@app.com")
    organizer = register_user(session, "org5@app.com", "password123", "organizer")

    # When: organizer attempts to apply
    try:
        apply_to_event(session, event, organizer, memo="Not allowed")
    except AuthorizationError as exc:
        # Then: authorization error
        assert str(exc) == "role_required_stallholder"
    else:
        raise AssertionError("AuthorizationError not raised")


def _create_application(session, organizer_email: str, stall_email: str):
    organizer = register_user(session, organizer_email, "password123", "organizer")
    now = datetime.now(timezone.utc)
    event = create_event(
        session,
        organizer,
        title="Event",
        description="Sample",
        region="Tokyo",
        venue_address="Shibuya",
        genre="food",
        start_date=now + timedelta(days=7),
        end_date=now + timedelta(days=8),
        application_deadline=now + timedelta(days=5),
        capacity=10,
    )
    event.status = "open"
    session.add(event)
    session.commit()
    session.refresh(event)
    stallholder = register_user(session, stall_email, "password123", "stallholder")
    application = apply_to_event(session, event, stallholder, memo="Join")
    return application, organizer


def test_decide_application_success(session):
    # Given: application for organizer's event
    application, organizer = _create_application(session, "org6@app.com", "stall6@app.com")

    # When: organizer approves application
    updated = decide_application(session, organizer, application.id, approved=True)

    # Then: status becomes approved
    assert updated.status == "approved"
    notif = session.exec(
        select(Notification).where(Notification.user_id == application.stallholder_id)
    ).first()
    assert notif is not None
    assert notif.event_type == "application_approved"


def test_decide_application_not_owned(session):
    # Given: application for organizer A's event
    application, _ = _create_application(session, "org7@app.com", "stall7@app.com")
    other = register_user(session, "org8@app.com", "password123", "organizer")

    # When: other organizer attempts approval
    try:
        decide_application(session, other, application.id, approved=True)
    except AuthorizationError as exc:
        # Then: authorization error
        assert str(exc) == "event_not_owned"
    else:
        raise AssertionError("AuthorizationError not raised")


def test_decide_application_already_cancelled(session):
    # Given: cancelled application
    application, organizer = _create_application(session, "org13@app.com", "stall13@app.com")
    from app.services.application_service import cancel_application
    from app.models import User

    stallholder = session.get(User, application.stallholder_id)
    cancel_application(session, stallholder, application.id)

    # When: organizer attempts to approve cancelled application
    try:
        decide_application(session, organizer, application.id, approved=True)
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "application_already_decided"
    else:
        raise AssertionError("ValidationError not raised")


def test_decide_application_already_approved(session):
    # Given: already approved application
    application, organizer = _create_application(session, "org14@app.com", "stall14@app.com")
    decide_application(session, organizer, application.id, approved=True)

    # When: organizer attempts to approve again
    try:
        decide_application(session, organizer, application.id, approved=True)
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "application_already_decided"
    else:
        raise AssertionError("ValidationError not raised")


def test_cancel_application_success(session):
    # Given: pending application
    application, _ = _create_application(session, "org9@app.com", "stall9@app.com")
    stallholder = session.get(User, application.stallholder_id)

    # When: cancelling application
    cancelled = cancel_application(session, stallholder, application.id)

    # Then: status becomes cancelled
    assert cancelled.status == "cancelled"


def test_cancel_application_not_owned(session):
    # Given: application owned by stallholder A
    application, _ = _create_application(session, "org10@app.com", "stall10@app.com")
    other = register_user(session, "stall11@app.com", "password123", "stallholder")

    # When: other stallholder attempts cancellation
    try:
        cancel_application(session, other, application.id)
    except AuthorizationError as exc:
        # Then: authorization error
        assert str(exc) == "application_not_owned"
    else:
        raise AssertionError("AuthorizationError not raised")


def test_cancel_application_already_rejected(session):
    # Given: rejected application
    application, organizer = _create_application(session, "org12@app.com", "stall12@app.com")
    decide_application(session, organizer, application.id, approved=False)
    stallholder = session.get(User, application.stallholder_id)

    # When: attempting to cancel rejected application
    try:
        cancel_application(session, stallholder, application.id)
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "application_not_cancellable"
    else:
        raise AssertionError("ValidationError not raised")
