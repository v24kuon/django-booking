from sqlmodel import Session, select

from app.models import AdminNote, Guide, Report


def save_report(session: Session, report: Report) -> Report:
    session.add(report)
    session.commit()
    session.refresh(report)
    return report


def list_reports(session: Session) -> list[Report]:
    statement = select(Report)
    return list(session.exec(statement).all())


def save_admin_note(session: Session, note: AdminNote) -> AdminNote:
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


def list_admin_notes(session: Session, target_type: str | None = None, target_id: int | None = None) -> list[AdminNote]:
    statement = select(AdminNote)
    if target_type:
        statement = statement.where(AdminNote.target_type == target_type)
    if target_id:
        statement = statement.where(AdminNote.target_id == target_id)
    return list(session.exec(statement).all())


def save_guide(session: Session, guide: Guide) -> Guide:
    session.add(guide)
    session.commit()
    session.refresh(guide)
    return guide
