from datetime import datetime, timedelta, timezone

from sqlmodel import select

from app.errors import AuthorizationError, ValidationError
from app.models import Report, StallholderProfile
from sqlmodel import select

from app.models import Notification
from app.services.admin_service import (
    approve_event,
    create_admin_note,
    create_guide,
    review_stallholder_profile,
    toggle_user_active,
    update_report_status,
)
from app.services.auth_service import register_user
from app.services.event_service import create_event


def _create_pending_event(session, organizer_email: str):
    organizer = register_user(session, organizer_email, "password123", "organizer")
    now = datetime.now(timezone.utc)
    event = create_event(
        session,
        organizer,
        title="Pending Event",
        description="Sample event",
        region="Tokyo",
        venue_address="Shibuya",
        genre="food",
        start_date=now + timedelta(days=7),
        end_date=now + timedelta(days=8),
        application_deadline=now + timedelta(days=5),
        capacity=10,
    )
    event.status = "pending_review"
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def test_admin_approve_event_success(session):
    # Given: admin and pending event
    event = _create_pending_event(session, "org@app.com")
    admin = register_user(session, "admin@app.com", "password123", "admin", allow_admin=True)

    # When: approving event
    updated = approve_event(session, admin, event, approve=True)

    # Then: status becomes open
    assert updated.status == "open"


def test_admin_approve_event_wrong_status(session):
    # Given: admin and non-pending event
    event = _create_pending_event(session, "org2@app.com")
    event.status = "draft"
    session.add(event)
    session.commit()
    admin = register_user(session, "admin2@app.com", "password123", "admin", allow_admin=True)

    # When: approving non-pending event
    try:
        approve_event(session, admin, event, approve=True)
    except ValidationError as exc:
        # Then: validation error
        assert str(exc) == "event_status_invalid"
    else:
        raise AssertionError("ValidationError not raised")


def test_admin_approve_event_wrong_role(session):
    # Given: non-admin user
    event = _create_pending_event(session, "org3@app.com")
    organizer = register_user(session, "org4@app.com", "password123", "organizer")

    # When: organizer attempts approval
    try:
        approve_event(session, organizer, event, approve=True)
    except AuthorizationError as exc:
        # Then: authorization error
        assert str(exc) == "role_required_admin"
    else:
        raise AssertionError("AuthorizationError not raised")


def test_review_stallholder_profile_success(session):
    # Given: admin and pending profile
    admin = register_user(session, "admin3@app.com", "password123", "admin", allow_admin=True)
    user = register_user(session, "stall10@app.com", "password123", "stallholder")
    profile = session.exec(
        select(StallholderProfile).where(StallholderProfile.user_id == user.id)
    ).first()

    # When: approving profile
    updated = review_stallholder_profile(
        session, admin, profile_id=profile.id, approved=True, review_note="ok"
    )

    # Then: status updated
    assert updated.review_status == "approved"


def test_update_report_status_success(session):
    # Given: report and admin
    admin = register_user(session, "admin4@app.com", "password123", "admin", allow_admin=True)
    report = Report(
        reporter_id=admin.id,
        target_type="event",
        target_id=1,
        status="open",
    )
    session.add(report)
    session.commit()
    session.refresh(report)

    # When: updating report status
    updated = update_report_status(
        session, admin, report_id=report.id, status="closed", resolution_note="done"
    )

    # Then: status updated
    assert updated.status == "closed"


def test_create_guide_success(session):
    # Given: admin
    admin = register_user(session, "admin5@app.com", "password123", "admin", allow_admin=True)

    # When: creating guide
    guide = create_guide(
        session,
        admin,
        target_role="stallholder",
        title="Guide",
        body="Body",
        publish=True,
    )

    # Then: guide created
    assert guide.id is not None
    assert guide.is_published is True


def test_create_admin_note_success(session):
    # Given: admin
    admin = register_user(session, "admin6@app.com", "password123", "admin", allow_admin=True)

    # When: creating note
    note = create_admin_note(session, admin, target_type="user", target_id=1, note="memo")

    # Then: note created
    assert note.id is not None


def test_toggle_user_active_success(session):
    # Given: admin and target user
    admin = register_user(session, "admin7@app.com", "password123", "admin", allow_admin=True)
    target = register_user(session, "stall11@app.com", "password123", "stallholder")

    # When: deactivating user
    updated = toggle_user_active(session, admin, user_id=target.id, is_active=False)

    # Then: user deactivated
    assert updated.is_active is False


def test_approve_event_notifies_organizer(session):
    # Given: pending event and admin
    event = _create_pending_event(session, "org13@app.com")
    admin = register_user(session, "admin8@app.com", "password123", "admin", allow_admin=True)

    # When: approving event
    updated = approve_event(session, admin, event, approve=True)

    # Then: organizer notified
    notif = session.exec(
        select(Notification).where(
            Notification.user_id == event.organizer_id, Notification.event_type == "event_updated"
        )
    ).first()
    assert notif is not None
