from datetime import datetime, timedelta, timezone

from sqlmodel import select

from app.errors import ValidationError
from app.models import Notification
from app.services.application_service import apply_to_event
from app.services.auth_service import register_user
from app.services.event_service import create_event
from app.services.message_service import send_message


def _create_approved_application(session):
    organizer = register_user(session, "org@app.com", "password123", "organizer")
    stallholder = register_user(session, "stall@app.com", "password123", "stallholder")
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
    application = apply_to_event(session, event, stallholder, memo="Join")
    application.status = "approved"
    session.add(application)
    session.commit()
    session.refresh(application)
    return application, stallholder


def test_send_message_success(session):
    # Given: approved application
    application, sender = _create_approved_application(session)

    # When: sending message
    message = send_message(session, application, sender, content="Hello")

    # Then: message created
    assert message.id is not None
    notif = session.exec(
        select(Notification).where(Notification.event_type == "message_received")
    ).first()
    assert notif is not None
    assert notif.event_type == "message_received"


def test_send_message_not_approved(session):
    # Given: pending application
    application, sender = _create_approved_application(session)
    application.status = "pending"
    session.add(application)
    session.commit()

    # When: sending message for pending application
    try:
        send_message(session, application, sender, content="Hi")
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "application_not_approved"
    else:
        raise AssertionError("ValidationError not raised")


def test_send_message_empty_content(session):
    # Given: approved application
    application, sender = _create_approved_application(session)

    # When: sending empty content
    try:
        send_message(session, application, sender, content="")
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "content_required"
    else:
        raise AssertionError("ValidationError not raised")
