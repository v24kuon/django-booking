from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.errors import ValidationError
from app.models import AdminNote, Application, Event, Guide, Report, Review, StallholderProfile, User
from app.repositories.admin_repo import list_admin_notes
from app.routes.deps import require_role, session_dependency
from app.services.admin_service import (
    approve_event,
    create_admin_note,
    create_guide,
    delete_guide,
    review_stallholder_profile,
    toggle_user_active,
    update_guide,
    update_report_status,
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


@router.get("")
def admin_dashboard(
    request: Request,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("admin")),
):
    pending_events = list(
        session.exec(select(Event).where(Event.status == "pending_review")).all()
    )
    reports = list(session.exec(select(Report)).all())
    pending_profiles = list(
        session.exec(select(StallholderProfile).where(StallholderProfile.review_status == "pending")).all()
    )
    guides = list(session.exec(select(Guide)).all())
    admin_notes = list_admin_notes(session)
    search_type = request.query_params.get("search_type", "")
    search_query = request.query_params.get("q", "")
    search_results = []
    if search_type and search_query:
        if search_type == "user":
            search_results = list(
                session.exec(
                    select(User).where(User.email.contains(search_query))
                ).all()
            )
        elif search_type == "event":
            search_results = list(
                session.exec(
                    select(Event).where(Event.title.contains(search_query))
                ).all()
            )
        elif search_type == "application":
            search_results = list(
                session.exec(select(Application)).all()
            )
        elif search_type == "review":
            search_results = list(
                session.exec(
                    select(Review).where(Review.comment.contains(search_query))
                ).all()
            )
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "pending_events": pending_events,
            "reports": reports,
            "pending_profiles": pending_profiles,
            "guides": guides,
            "admin_notes": admin_notes,
            "user": user,
            "search_type": search_type,
            "search_query": search_query,
            "search_results": search_results,
        },
    )


@router.post("/events/{event_id}/approve")
def approve_event_action(
    event_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("admin")),
):
    event = session.get(Event, event_id)
    if not event:
        return RedirectResponse(url="/admin", status_code=303)
    try:
        approve_event(session, user, event, approve=True)
    except ValidationError:
        pass
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/events/{event_id}/reject")
def reject_event_action(
    event_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("admin")),
):
    event = session.get(Event, event_id)
    if not event:
        return RedirectResponse(url="/admin", status_code=303)
    try:
        approve_event(session, user, event, approve=False)
    except ValidationError:
        pass
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/profiles/{profile_id}/approve")
def approve_profile_action(
    profile_id: int,
    note: str = Form(""),
    session: Session = Depends(session_dependency),
    user=Depends(require_role("admin")),
):
    try:
        review_stallholder_profile(session, user, profile_id, approved=True, review_note=note or None)
    except ValidationError:
        pass
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/profiles/{profile_id}/reject")
def reject_profile_action(
    profile_id: int,
    note: str = Form(""),
    session: Session = Depends(session_dependency),
    user=Depends(require_role("admin")),
):
    try:
        review_stallholder_profile(session, user, profile_id, approved=False, review_note=note or None)
    except ValidationError:
        pass
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/reports/{report_id}/status")
def update_report(
    report_id: int,
    status: str = Form(...),
    resolution_note: str = Form(""),
    session: Session = Depends(session_dependency),
    user=Depends(require_role("admin")),
):
    try:
        update_report_status(
            session, user, report_id=report_id, status=status, resolution_note=resolution_note or None
        )
    except ValidationError:
        pass
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/notes")
def create_note(
    target_type: str = Form(...),
    target_id: int = Form(...),
    note: str = Form(...),
    session: Session = Depends(session_dependency),
    user=Depends(require_role("admin")),
):
    try:
        create_admin_note(session, user, target_type=target_type, target_id=target_id, note=note)
    except ValidationError:
        pass
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/guides")
def create_guide_action(
    target_role: str = Form(...),
    title: str = Form(...),
    body: str = Form(...),
    publish: bool = Form(False),
    session: Session = Depends(session_dependency),
    user=Depends(require_role("admin")),
):
    try:
        create_guide(
            session,
            user,
            target_role=target_role,
            title=title,
            body=body,
            publish=publish,
        )
    except ValidationError:
        pass
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/users/toggle")
def toggle_user(
    user_id: int = Form(...),
    is_active: bool = Form(...),
    session: Session = Depends(session_dependency),
    user=Depends(require_role("admin")),
):
    try:
        toggle_user_active(session, user, user_id=user_id, is_active=is_active)
    except ValidationError:
        pass
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/guides/{guide_id}/update")
def update_guide_action(
    guide_id: int,
    title: str = Form(...),
    body: str = Form(...),
    publish: bool = Form(False),
    session: Session = Depends(session_dependency),
    user=Depends(require_role("admin")),
):
    try:
        update_guide(session, user, guide_id=guide_id, title=title, body=body, publish=publish)
    except ValidationError:
        pass
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/guides/{guide_id}/delete")
def delete_guide_action(
    guide_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("admin")),
):
    try:
        delete_guide(session, user, guide_id=guide_id)
    except ValidationError:
        pass
    return RedirectResponse(url="/admin", status_code=303)
