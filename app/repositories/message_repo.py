from sqlmodel import Session, select

from app.models import Message


def list_messages_for_application(session: Session, application_id: int) -> list[Message]:
    statement = select(Message).where(Message.application_id == application_id)
    return list(session.exec(statement).all())


def save_message(session: Session, message: Message) -> Message:
    session.add(message)
    session.commit()
    session.refresh(message)
    return message
