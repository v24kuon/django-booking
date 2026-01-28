from sqlmodel import Session, select

from app.models import Event


def get_event(session: Session, event_id: int) -> Event | None:
    return session.get(Event, event_id)


def list_events(session: Session) -> list[Event]:
    statement = select(Event)
    return list(session.exec(statement).all())


def save_event(session: Session, event: Event) -> Event:
    session.add(event)
    session.commit()
    session.refresh(event)
    return event
