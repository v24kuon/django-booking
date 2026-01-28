from datetime import datetime, timezone

from sqlmodel import Session

from app.errors import ValidationError
from app.models import Application, Event, Message, User
from app.repositories.message_repo import save_message
from app.services.notification_service import create_notification


def send_message(
    session: Session, application: Application, sender: User, content: str
) -> Message:
    if application.status != "approved":
        raise ValidationError("application_not_approved")
    if not content:
        raise ValidationError("content_required")

    message = Message(
        application_id=application.id,
        sender_id=sender.id,
        content=content,
        created_at=datetime.now(timezone.utc),
    )
    message = save_message(session, message)

    event = session.get(Event, application.event_id)
    recipient_id = None
    if sender.role == "stallholder" and event:
        recipient_id = event.organizer_id
    elif sender.role == "organizer":
        recipient_id = application.stallholder_id
    if recipient_id:
        recipient = session.get(User, recipient_id)
        if recipient:
            create_notification(
                session,
                recipient,
                event_type="message_received",
                title="新しいメッセージが届きました",
                body=content[:50],
                related_type="message",
                related_id=message.id,
            )
    return message
