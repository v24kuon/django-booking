from datetime import datetime, timezone

from sqlmodel import Session

from app.models import Notification, User
from app.repositories.notification_repo import save_notification


def create_notification(
    session: Session,
    user: User,
    event_type: str,
    title: str,
    body: str,
    channel: str = "in_app",
    related_type: str | None = None,
    related_id: int | None = None,
) -> Notification:
    notification = Notification(
        user_id=user.id,
        event_type=event_type,
        channel=channel,
        title=title,
        body=body,
        related_type=related_type,
        related_id=related_id,
        delivery_status="queued",
        created_at=datetime.now(timezone.utc),
    )
    return save_notification(session, notification)


def mark_notification_read(session: Session, notification: Notification) -> Notification:
    notification.is_read = True
    notification.read_at = datetime.now(timezone.utc)
    return save_notification(session, notification)
