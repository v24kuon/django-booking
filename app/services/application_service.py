from datetime import datetime, timezone

from sqlmodel import Session

from app.errors import AuthorizationError, ValidationError
from app.models import Application, Event, User
from app.repositories.application_repo import (
    find_application,
    get_application,
    save_application,
)
from app.services.event_service import get_event_for_organizer
from app.services.notification_service import create_notification


def apply_to_event(
    session: Session, event: Event, stallholder: User, memo: str | None
) -> Application:
    if stallholder.role != "stallholder":
        raise AuthorizationError("role_required_stallholder")
    if event.status != "open":
        raise ValidationError("event_not_open")

    existing = find_application(session, event.id, stallholder.id)
    if existing:
        raise ValidationError("application_exists")

    application = Application(
        event_id=event.id,
        stallholder_id=stallholder.id,
        memo=memo,
        status="pending",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    application = save_application(session, application)

    organizer = session.get(User, event.organizer_id)
    if organizer:
        create_notification(
            session,
            organizer,
            event_type="application_submitted",
            title="新しい応募が届きました",
            body=f"イベント: {event.title}",
            related_type="application",
            related_id=application.id,
        )
    return application


def decide_application(
    session: Session, organizer: User, application_id: int, approved: bool
) -> Application:
    application = get_application(session, application_id)
    if not application:
        raise ValidationError("application_not_found")
    get_event_for_organizer(session, organizer, application.event_id)
    
    # キャンセル済みや既に決定済みの応募は処理できない
    if application.status not in {"pending"}:
        raise ValidationError("application_already_decided")
    
    application.status = "approved" if approved else "rejected"
    application.decided_at = datetime.now(timezone.utc)
    application.updated_at = datetime.now(timezone.utc)
    application = save_application(session, application)

    stallholder = session.get(User, application.stallholder_id)
    if stallholder:
        create_notification(
            session,
            stallholder,
            event_type="application_approved" if approved else "application_rejected",
            title="応募結果が更新されました",
            body="応募結果を確認してください。",
            related_type="application",
            related_id=application.id,
        )
    return application


def cancel_application(
    session: Session, stallholder: User, application_id: int
) -> Application:
    if stallholder.role != "stallholder":
        raise AuthorizationError("role_required_stallholder")
    application = get_application(session, application_id)
    if not application:
        raise ValidationError("application_not_found")
    if application.stallholder_id != stallholder.id:
        raise AuthorizationError("application_not_owned")
    if application.status not in {"pending", "approved"}:
        raise ValidationError("application_not_cancellable")

    application.status = "cancelled"
    application.updated_at = datetime.now(timezone.utc)
    application = save_application(session, application)

    event = session.get(Event, application.event_id)
    if event:
        organizer = session.get(User, event.organizer_id)
        if organizer:
            create_notification(
                session,
                organizer,
                event_type="application_cancelled",
                title="応募がキャンセルされました",
                body=f"イベント「{event.title}」への応募がキャンセルされました。",
                related_type="application",
                related_id=application.id,
            )

    return application
