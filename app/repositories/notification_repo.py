from sqlmodel import Session, select

from app.models import Notification


def list_notifications_for_user(session: Session, user_id: int) -> list[Notification]:
    statement = select(Notification).where(Notification.user_id == user_id)
    return list(session.exec(statement).all())


def save_notification(session: Session, notification: Notification) -> Notification:
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification
