from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.errors import AuthorizationError, ValidationError
from app.models import Application, Event, StallholderProfile
from app.routes.deps import require_role, session_dependency
from app.services.application_service import apply_to_event, cancel_application
from app.services.event_service import search_events
from app.services.profile_service import update_stallholder_profile
from app.services.review_service import create_review
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
def dashboard(
    request: Request,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("stallholder")),
):
    region = request.query_params.get("region") or None
    genre = request.query_params.get("genre") or None
    date_str = request.query_params.get("date") or None
    date_value: date | None = None
    if date_str:
        try:
            date_value = date.fromisoformat(date_str)
        except ValueError:
            date_value = None

    events = search_events(session, region=region, genre=genre, date_value=date_value)
    regions = list(
        {
            value
            for value in session.exec(
                select(Event.region).where(Event.status == "open").distinct()
            ).all()
            if value
        }
    )
    genres = list(
        {
            value
            for value in session.exec(
                select(Event.genre).where(Event.status == "open").distinct()
            ).all()
            if value
        }
    )
    return templates.TemplateResponse(
        "stallholder/dashboard.html",
        {
            "request": request,
            "events": events,
            "user": user,
            "regions": sorted(regions),
            "genres": sorted(genres),
            "selected_region": region or "",
            "selected_genre": genre or "",
            "selected_date": date_str or "",
        },
    )


@router.get("/events/{event_id}")
def event_detail(
    request: Request,
    event_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("stallholder")),
):
    event = session.get(Event, event_id)
    if not event:
        return RedirectResponse(url="/stallholder", status_code=303)

    # 既に応募済みかどうかを確認
    from app.repositories.application_repo import find_application
    existing_application = find_application(session, event.id, user.id)

    # エラーメッセージを取得（セッションから）
    error_message = request.session.pop("error_message", None)

    return templates.TemplateResponse(
        "stallholder/event_detail.html",
        {
            "request": request,
            "event": event,
            "user": user,
            "existing_application": existing_application,
            "error_message": error_message,
        },
    )


@router.post("/events/{event_id}/apply")
def apply_event(
    request: Request,
    event_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("stallholder")),
):
    event = session.get(Event, event_id)
    if not event:
        return RedirectResponse(url="/stallholder", status_code=303)

    try:
        apply_to_event(session, event, user, memo=None)
        # 成功時はエラーメッセージをクリア
        request.session.pop("error_message", None)
        return RedirectResponse(url="/stallholder/applications", status_code=303)
    except ValidationError as exc:
        # エラーメッセージをセッションに保存
        error_messages = {
            "event_not_open": "このイベントは現在応募を受け付けていません。",
            "application_exists": "既にこのイベントに応募済みです。",
        }
        request.session["error_message"] = error_messages.get(str(exc), "応募に失敗しました。")
        return RedirectResponse(url=f"/stallholder/events/{event_id}", status_code=303)
    except AuthorizationError as exc:
        request.session["error_message"] = "応募する権限がありません。"
        return RedirectResponse(url=f"/stallholder/events/{event_id}", status_code=303)


@router.get("/applications")
def applications(
    request: Request,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("stallholder")),
):
    statement = select(Application).where(Application.stallholder_id == user.id)
    apps = list(session.exec(statement).all())
    return templates.TemplateResponse(
        "stallholder/applications.html",
        {"request": request, "applications": apps, "user": user},
    )


@router.post("/applications/{application_id}/cancel")
def cancel_application_action(
    application_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("stallholder")),
):
    try:
        cancel_application(session, user, application_id)
    except (ValidationError, AuthorizationError):
        pass
    return RedirectResponse(url="/stallholder/applications", status_code=303)


@router.get("/profile")
def profile_page(
    request: Request,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("stallholder")),
):
    profile = session.exec(
        select(StallholderProfile).where(StallholderProfile.user_id == user.id)
    ).first()
    if not profile:
        return RedirectResponse(url="/stallholder", status_code=303)
    return templates.TemplateResponse(
        "stallholder/profile.html",
        {"request": request, "profile": profile, "user": user},
    )


@router.post("/profile")
def profile_update(
    request: Request,
    business_name: str = Form(...),
    genre: str = Form(...),
    bio: str = Form(...),
    website_url: str = Form(""),
    past_achievements: str = Form(""),
    session: Session = Depends(session_dependency),
    user=Depends(require_role("stallholder")),
):
    try:
        update_stallholder_profile(
            session,
            user,
            business_name=business_name,
            genre=genre,
            bio=bio,
            website_url=website_url or None,
            past_achievements=past_achievements or None,
        )
    except (AuthorizationError, ValidationError) as exc:
        return templates.TemplateResponse(
            "stallholder/profile.html",
            {
                "request": request,
                "profile": {
                    "business_name": business_name,
                    "genre": genre,
                    "bio": bio,
                    "website_url": website_url,
                    "past_achievements": past_achievements,
                    "review_status": "pending",
                    "review_note": None,
                },
                "user": user,
                "error": str(exc),
            },
            status_code=400,
        )
    return RedirectResponse(url="/stallholder/profile", status_code=303)


@router.get("/reviews/{application_id}/new")
def new_review_page(
    request: Request,
    application_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(require_role("stallholder")),
):
    application = session.get(Application, application_id)
    if not application or application.stallholder_id != user.id:
        return RedirectResponse(url="/stallholder/applications", status_code=303)
    event = session.get(Event, application.event_id)
    if not event:
        return RedirectResponse(url="/stallholder/applications", status_code=303)
    organizer = session.get(User, event.organizer_id)
    if not organizer:
        return RedirectResponse(url="/stallholder/applications", status_code=303)
    return templates.TemplateResponse(
        "stallholder/new_review.html",
        {
            "request": request,
            "application": application,
            "event": event,
            "target": organizer,
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
    user=Depends(require_role("stallholder")),
):
    application = session.get(Application, application_id)
    if not application or application.stallholder_id != user.id:
        return RedirectResponse(url="/stallholder/applications", status_code=303)
    event = session.get(Event, application.event_id)
    if not event:
        return RedirectResponse(url="/stallholder/applications", status_code=303)
    organizer = session.get(User, event.organizer_id)
    if not organizer:
        return RedirectResponse(url="/stallholder/applications", status_code=303)
    try:
        create_review(session, application, user, organizer, score, comment)
    except ValidationError:
        return RedirectResponse(url=f"/stallholder/reviews/{application_id}/new", status_code=303)
    return RedirectResponse(url="/stallholder/applications", status_code=303)
