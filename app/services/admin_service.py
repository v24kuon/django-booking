from datetime import datetime, timezone

from sqlmodel import Session

from app.errors import AuthorizationError, ValidationError
from app.models import AdminNote, Event, Guide, Report, StallholderProfile, User
from app.repositories.admin_repo import save_admin_note, save_guide, save_report
from app.repositories.event_repo import save_event
from app.services.notification_service import create_notification


def approve_event(session: Session, admin: User, event: Event, approve: bool) -> Event:
    if admin.role != "admin":
        raise AuthorizationError("role_required_admin")
    if event.status != "pending_review":
        raise ValidationError("event_status_invalid")

    event.status = "open" if approve else "closed"
    event.updated_at = datetime.now(timezone.utc)
    event = save_event(session, event)

    organizer = session.get(User, event.organizer_id)
    if organizer:
        create_notification(
            session,
            organizer,
            event_type="event_updated" if approve else "event_rejected",
            title="イベント審査結果",
            body=f"イベント「{event.title}」の審査が完了しました。",
            related_type="event",
            related_id=event.id,
        )
    return event


def review_stallholder_profile(
    session: Session,
    admin: User,
    profile_id: int,
    approved: bool,
    review_note: str | None,
) -> StallholderProfile:
    if admin.role != "admin":
        raise AuthorizationError("role_required_admin")
    profile = session.get(StallholderProfile, profile_id)
    if not profile:
        raise ValidationError("profile_not_found")

    profile.review_status = "approved" if approved else "rejected"
    profile.reviewed_by = admin.id
    profile.reviewed_at = datetime.now(timezone.utc)
    profile.review_note = review_note
    profile.updated_at = datetime.now(timezone.utc)
    session.add(profile)
    session.commit()
    session.refresh(profile)

    target = session.get(User, profile.user_id)
    if target:
        create_notification(
            session,
            target,
            event_type="moderation_result",
            title="プロフィール審査結果",
            body="プロフィール審査の結果が更新されました。",
            related_type="stallholder_profile",
            related_id=profile.id,
        )
    return profile


def update_report_status(
    session: Session,
    admin: User,
    report_id: int,
    status: str,
    resolution_note: str | None,
) -> Report:
    if admin.role != "admin":
        raise AuthorizationError("role_required_admin")
    report = session.get(Report, report_id)
    if not report:
        raise ValidationError("report_not_found")
    if status not in {"open", "in_progress", "closed"}:
        raise ValidationError("report_status_invalid")
    report.status = status
    report.resolution_note = resolution_note
    report.handled_by = admin.id
    report.handled_at = datetime.now(timezone.utc)
    report.updated_at = datetime.now(timezone.utc)
    return save_report(session, report)


def create_admin_note(
    session: Session,
    admin: User,
    target_type: str,
    target_id: int,
    note: str,
) -> AdminNote:
    if admin.role != "admin":
        raise AuthorizationError("role_required_admin")
    if target_type not in {"user", "event"}:
        raise ValidationError("note_target_invalid")
    admin_note = AdminNote(
        author_id=admin.id,
        target_type=target_type,
        target_id=target_id,
        note=note,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    return save_admin_note(session, admin_note)


def create_guide(
    session: Session,
    admin: User,
    target_role: str,
    title: str,
    body: str,
    publish: bool,
) -> Guide:
    if admin.role != "admin":
        raise AuthorizationError("role_required_admin")
    if target_role not in {"stallholder", "organizer", "all"}:
        raise ValidationError("guide_role_invalid")
    guide = Guide(
        target_role=target_role,
        title=title,
        body=body,
        is_published=publish,
        published_at=datetime.now(timezone.utc) if publish else None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    return save_guide(session, guide)


def toggle_user_active(session: Session, admin: User, user_id: int, is_active: bool) -> User:
    if admin.role != "admin":
        raise AuthorizationError("role_required_admin")
    target = session.get(User, user_id)
    if not target:
        raise ValidationError("user_not_found")
    target.is_active = is_active
    target.updated_at = datetime.now(timezone.utc)
    session.add(target)
    session.commit()
    session.refresh(target)
    return target


def update_guide(
    session: Session,
    admin: User,
    guide_id: int,
    title: str,
    body: str,
    publish: bool,
) -> Guide:
    if admin.role != "admin":
        raise AuthorizationError("role_required_admin")
    guide = session.get(Guide, guide_id)
    if not guide:
        raise ValidationError("guide_not_found")
    guide.title = title
    guide.body = body
    guide.is_published = publish
    guide.published_at = datetime.now(timezone.utc) if publish else None
    guide.updated_at = datetime.now(timezone.utc)
    return save_guide(session, guide)


def delete_guide(session: Session, admin: User, guide_id: int) -> None:
    if admin.role != "admin":
        raise AuthorizationError("role_required_admin")
    guide = session.get(Guide, guide_id)
    if not guide:
        raise ValidationError("guide_not_found")
    session.delete(guide)
    session.commit()
