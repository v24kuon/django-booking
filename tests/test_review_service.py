from datetime import datetime, timedelta, timezone

from sqlmodel import select

from app.errors import ValidationError
from app.models import Notification
from app.services.application_service import apply_to_event
from app.services.auth_service import register_user
from app.services.event_service import create_event
from app.services.review_service import create_review


def _create_application(session):
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
    return application, organizer, stallholder


def test_create_review_success(session):
    # Given: application and reviewer
    application, organizer, stallholder = _create_application(session)

    # When: organizer reviews stallholder
    review = create_review(
        session,
        application=application,
        author=organizer,
        target=stallholder,
        score=5,
        comment="Great",
    )

    # Then: review created
    assert review.id is not None
    notif = session.exec(
        select(Notification).where(Notification.user_id == stallholder.id)
    ).first()
    assert notif is not None
    assert notif.event_type == "review_posted"


def test_create_review_duplicate(session):
    # Given: existing review
    application, organizer, stallholder = _create_application(session)
    create_review(
        session,
        application=application,
        author=organizer,
        target=stallholder,
        score=5,
        comment="Great",
    )

    # When: submitting duplicate review
    try:
        create_review(
            session,
            application=application,
            author=organizer,
            target=stallholder,
            score=4,
            comment="Again",
        )
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "review_exists"
    else:
        raise AssertionError("ValidationError not raised")


def test_create_review_score_zero(session):
    # Given: application and reviewer
    application, organizer, stallholder = _create_application(session)

    # When: submitting score=0
    try:
        create_review(
            session,
            application=application,
            author=organizer,
            target=stallholder,
            score=0,
            comment="Bad",
        )
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "score_invalid"
    else:
        raise AssertionError("ValidationError not raised")


def test_create_review_low_rating_notifies_organizer(session):
    # Given: application and reviewer
    application, organizer, stallholder = _create_application(session)

    # When: submitting low rating (<=2)
    review = create_review(
        session,
        application=application,
        author=organizer,
        target=stallholder,
        score=2,
        comment="Low",
    )

    # Then: organizer notified
    notif = session.exec(
        select(Notification).where(
            Notification.user_id == organizer.id, Notification.event_type == "low_rating"
        )
    ).first()
    assert notif is not None
