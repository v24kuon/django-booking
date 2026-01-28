from sqlmodel import Session, select

from app.models import Application


def get_application(session: Session, application_id: int) -> Application | None:
    return session.get(Application, application_id)


def find_application(
    session: Session, event_id: int, stallholder_id: int
) -> Application | None:
    statement = select(Application).where(
        Application.event_id == event_id,
        Application.stallholder_id == stallholder_id,
    )
    return session.exec(statement).first()


def save_application(session: Session, application: Application) -> Application:
    session.add(application)
    session.commit()
    session.refresh(application)
    return application
