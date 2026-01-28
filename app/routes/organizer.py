from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlmodel import Session, select

from app.errors import AuthorizationError, ValidationError
from app.models import Application, Event
from app.routes.deps import require_role, session_dependency
from app.services.application_service import decide_application
from app.services.review_service import create_review
from app.services.event_service import (
    create_event,
    get_event_for_organizer,
    submit_event_for_review,
    update_event,
)
from app.utils import (
    APPLICATION_STATUS_LABELS,
    EVENT_STATUS_LABELS,
    PROFILE_REVIEW_STATUS_LABELS,
    REPORT_STATUS_LABELS,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["event_status_labels"] = EVENT_STATUS_LABELS
templates.env.globals["app_status_labels"] = APPLICATION_STATUS_LABELS
templates.env.globals["report_status_labels"] = REPORT_STATUS_LABELS
templates.env.globals["profile_review_status_labels"] = PROFILE_REVIEW_STATUS_LABELS


def _to_datetime_local(value: datetime) -> str:
    return value.replace(tzinfo=None).strftime("%Y-%m-%dT%H:%M")


@router.get("")
def dashboard(
    request: Request,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("organizer")),
):
    statement = select(Event).where(Event.organizer_id == user.id)
    events = list(session.exec(statement).all())
    counts: dict[int, int] = {}
    status_counts: dict[str, int] = {}
    for event in events:
        status_counts[event.status] = status_counts.get(event.status, 0) + 1
    if events:
        ids = [event.id for event in events if event.id is not None]
        if ids:
            count_stmt = (
                select(Application.event_id, func.count())
                .where(Application.event_id.in_(ids))
                .group_by(Application.event_id)
            )
            counts = {row[0]: row[1] for row in session.exec(count_stmt).all()}
    return templates.TemplateResponse(
        "organizer/dashboard.html",
        {
            "request": request,
            "events": events,
            "user": user,
            "application_counts": counts,
            "status_counts": status_counts,
        },
    )


@router.get("/events/new")
def new_event_page(
    request: Request,
    user=Depends(require_role("organizer")),
):
    return templates.TemplateResponse(
        "organizer/new_event.html", {"request": request, "user": user}
    )


@router.post("/events")
def create_event_action(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    region: str = Form(...),
    venue_address: str = Form(...),
    genre: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    application_deadline: str = Form(...),
    capacity: int = Form(...),
    session: Session = Depends(session_dependency),
    user=Depends(require_role("organizer")),
):
    try:
        event = create_event(
            session,
            user,
            title=title,
            description=description,
            region=region,
            venue_address=venue_address,
            genre=genre,
            start_date=datetime.fromisoformat(start_date),
            end_date=datetime.fromisoformat(end_date),
            application_deadline=datetime.fromisoformat(application_deadline),
            capacity=capacity,
        )
    except ValidationError as exc:
        return templates.TemplateResponse(
            "organizer/new_event.html",
            {"request": request, "error": str(exc), "user": user},
            status_code=400,
        )
    return RedirectResponse(url=f"/organizer/events/{event.id}", status_code=303)


@router.get("/events/{event_id}")
def event_detail(
    request: Request,
    event_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("organizer")),
):
    try:
        event = get_event_for_organizer(session, user, event_id)
    except (AuthorizationError, ValidationError):
        return RedirectResponse(url="/organizer", status_code=303)
    return templates.TemplateResponse(
        "organizer/event_detail.html",
        {"request": request, "event": event, "user": user},
    )


@router.get("/events/{event_id}/edit")
def edit_event_page(
    request: Request,
    event_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("organizer")),
):
    try:
        event = get_event_for_organizer(session, user, event_id)
    except (AuthorizationError, ValidationError):
        return RedirectResponse(url="/organizer", status_code=303)
    return templates.TemplateResponse(
        "organizer/edit_event.html",
        {
            "request": request,
            "event": event,
            "user": user,
            "start_date_value": _to_datetime_local(event.start_date),
            "end_date_value": _to_datetime_local(event.end_date),
            "deadline_value": _to_datetime_local(event.application_deadline),
        },
    )


@router.post("/events/{event_id}/edit")
def edit_event_action(
    request: Request,
    event_id: int,
    title: str = Form(...),
    description: str = Form(...),
    region: str = Form(...),
    venue_address: str = Form(...),
    genre: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    application_deadline: str = Form(...),
    capacity: int = Form(...),
    session: Session = Depends(session_dependency),
    user=Depends(require_role("organizer")),
):
    try:
        event = update_event(
            session,
            user,
            event_id=event_id,
            title=title,
            description=description,
            region=region,
            venue_address=venue_address,
            genre=genre,
            start_date=datetime.fromisoformat(start_date),
            end_date=datetime.fromisoformat(end_date),
            application_deadline=datetime.fromisoformat(application_deadline),
            capacity=capacity,
        )
    except (AuthorizationError, ValidationError) as exc:
        return templates.TemplateResponse(
            "organizer/edit_event.html",
            {
                "request": request,
                "event": {"id": event_id},
                "user": user,
                "error": str(exc),
                "title": title,
                "description": description,
                "region": region,
                "venue_address": venue_address,
                "genre": genre,
                "start_date_value": start_date,
                "end_date_value": end_date,
                "deadline_value": application_deadline,
                "capacity": capacity,
            },
            status_code=400,
        )
    return RedirectResponse(url=f"/organizer/events/{event.id}", status_code=303)


@router.post("/events/{event_id}/submit")
def submit_for_review(
    event_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("organizer")),
):
    try:
        submit_event_for_review(session, user, event_id=event_id)
    except (AuthorizationError, ValidationError):
        return RedirectResponse(url="/organizer", status_code=303)
    return RedirectResponse(url=f"/organizer/events/{event_id}", status_code=303)


@router.get("/events/{event_id}/applications")
def list_applications(
    request: Request,
    event_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("organizer")),
):
    try:
        event = get_event_for_organizer(session, user, event_id)
    except (AuthorizationError, ValidationError):
        return RedirectResponse(url="/organizer", status_code=303)
    statement = select(Application).where(Application.event_id == event.id)
    apps = list(session.exec(statement).all())
    return templates.TemplateResponse(
        "organizer/applications.html",
        {
            "request": request,
            "applications": apps,
            "user": user,
            "event": event,
        },
    )


@router.post("/applications/{application_id}/approve")
def approve_application(
    application_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("organizer")),
):
    try:
        decide_application(session, user, application_id, approved=True)
    except (AuthorizationError, ValidationError):
        return RedirectResponse(url="/organizer", status_code=303)
    return RedirectResponse(url="/organizer", status_code=303)


@router.post("/applications/{application_id}/reject")
def reject_application(
    application_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("organizer")),
):
    try:
        decide_application(session, user, application_id, approved=False)
    except (AuthorizationError, ValidationError):
        return RedirectResponse(url="/organizer", status_code=303)
    return RedirectResponse(url="/organizer", status_code=303)


@router.get("/reviews/{application_id}/new")
def new_review_page(
    request: Request,
    application_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("organizer")),
):
    application = session.get(Application, application_id)
    if not application:
        return RedirectResponse(url="/organizer", status_code=303)
    event = session.get(Event, application.event_id)
    if not event or event.organizer_id != user.id:
        return RedirectResponse(url="/organizer", status_code=303)
    from app.models import User as UserModel

    stallholder = session.get(UserModel, application.stallholder_id)
    if not stallholder:
        return RedirectResponse(url="/organizer", status_code=303)
    return templates.TemplateResponse(
        "organizer/new_review.html",
        {
            "request": request,
            "application": application,
            "event": event,
            "target": stallholder,
            "user": user,
        },
    )


@router.post("/reviews/{application_id}")
def create_review_action(
    request: Request,
    application_id: int,
    score: int = Form(...),
    comment: str = Form(...),
    session: Session = Depends(session_dependency),
    user=Depends(require_role("organizer")),
):
    application = session.get(Application, application_id)
    if not application:
        return RedirectResponse(url="/organizer", status_code=303)
    event = session.get(Event, application.event_id)
    if not event or event.organizer_id != user.id:
        return RedirectResponse(url="/organizer", status_code=303)
    from app.models import User as UserModel

    stallholder = session.get(UserModel, application.stallholder_id)
    if not stallholder:
        return RedirectResponse(url="/organizer", status_code=303)
    try:
        create_review(session, application, user, stallholder, score, comment)
    except ValidationError:
        return RedirectResponse(url=f"/organizer/reviews/{application_id}/new", status_code=303)
    return RedirectResponse(url="/organizer", status_code=303)
