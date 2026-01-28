from datetime import date, datetime, timezone

from sqlalchemy import func
from sqlmodel import Session, select

from app.errors import AuthorizationError, ValidationError
from app.models import Event, User
from app.repositories.event_repo import save_event
from app.services.notification_service import create_notification


def _validate_event_fields(
    title: str,
    capacity: int,
    start_date: datetime,
    end_date: datetime,
    application_deadline: datetime,
) -> None:
    if not title:
        raise ValidationError("title_required")
    if capacity < 1:
        raise ValidationError("capacity_invalid")
    if end_date < start_date:
        raise ValidationError("date_order_invalid")
    if application_deadline > start_date:
        raise ValidationError("deadline_invalid")


def get_event_for_organizer(session: Session, organizer: User, event_id: int) -> Event:
    if organizer.role != "organizer":
        raise AuthorizationError("role_required_organizer")
    event = session.get(Event, event_id)
    if not event:
        raise ValidationError("event_not_found")
    if event.organizer_id != organizer.id:
        raise AuthorizationError("event_not_owned")
    return event


def create_event(
    session: Session,
    organizer: User,
    title: str,
    description: str,
    region: str,
    venue_address: str,
    genre: str,
    start_date: datetime,
    end_date: datetime,
    application_deadline: datetime,
    capacity: int,
) -> Event:
    if organizer.role != "organizer":
        raise AuthorizationError("role_required_organizer")
    _validate_event_fields(title, capacity, start_date, end_date, application_deadline)

    event = Event(
        organizer_id=organizer.id,
        title=title,
        description=description,
        region=region,
        venue_address=venue_address,
        genre=genre,
        start_date=start_date,
        end_date=end_date,
        application_deadline=application_deadline,
        capacity=capacity,
        status="draft",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    return save_event(session, event)


def update_event(
    session: Session,
    organizer: User,
    event_id: int,
    title: str,
    description: str,
    region: str,
    venue_address: str,
    genre: str,
    start_date: datetime,
    end_date: datetime,
    application_deadline: datetime,
    capacity: int,
) -> Event:
    event = get_event_for_organizer(session, organizer, event_id)
    if event.status != "draft":
        raise ValidationError("event_not_editable")

    _validate_event_fields(title, capacity, start_date, end_date, application_deadline)

    event.title = title
    event.description = description
    event.region = region
    event.venue_address = venue_address
    event.genre = genre
    event.start_date = start_date
    event.end_date = end_date
    event.application_deadline = application_deadline
    event.capacity = capacity
    event.updated_at = datetime.now(timezone.utc)
    event = save_event(session, event)

    if event.status == "open":
        from app.models import Application

        applications = list(
            session.exec(
                select(Application).where(
                    Application.event_id == event.id, Application.status == "approved"
                )
            ).all()
        )
        for app in applications:
            stallholder = session.get(User, app.stallholder_id)
            if stallholder:
                create_notification(
                    session,
                    stallholder,
                    event_type="event_updated",
                    title="イベント情報が更新されました",
                    body=f"イベント「{event.title}」の情報が更新されました。",
                    related_type="event",
                    related_id=event.id,
                )
    return event


def submit_event_for_review(
    session: Session, organizer: User, event_id: int
) -> Event:
    event = get_event_for_organizer(session, organizer, event_id)
    if event.status != "draft":
        raise ValidationError("event_status_invalid")
    event.status = "pending_review"
    event.updated_at = datetime.now(timezone.utc)
    return save_event(session, event)


def search_events(
    session: Session, region: str | None, genre: str | None, date_value: date | None
) -> list[Event]:
    statement = select(Event).where(Event.status == "open")
    if region:
        statement = statement.where(Event.region == region)
    if genre:
        statement = statement.where(Event.genre == genre)
    if date_value:
        statement = statement.where(func.date(Event.start_date) <= date_value).where(
            func.date(Event.end_date) >= date_value
        )
    return list(session.exec(statement).all())
