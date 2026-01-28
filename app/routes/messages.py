from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.errors import ValidationError
from app.models import Application, Event
from app.repositories.message_repo import list_messages_for_application
from app.routes.deps import get_current_user, session_dependency
from app.services.message_service import send_message

router = APIRouter(prefix="/messages", tags=["messages"])
templates = Jinja2Templates(directory="app/templates")


def _load_application(session: Session, application_id: int) -> Application:
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="application_not_found")
    return application


def _authorize(session: Session, user, application: Application) -> Event:
    event = session.get(Event, application.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event_not_found")
    if user.role == "stallholder" and application.stallholder_id != user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    if user.role == "organizer" and event.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    if user.role not in {"stallholder", "organizer"}:
        raise HTTPException(status_code=403, detail="forbidden")
    if application.status != "approved":
        raise HTTPException(status_code=400, detail="application_not_approved")
    return event


@router.get("/{application_id}")
def message_room(
    request: Request,
    application_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(get_current_user),
):
    application = _load_application(session, application_id)
    event = _authorize(session, user, application)
    messages = list_messages_for_application(session, application.id)
    return templates.TemplateResponse(
        "messages/room.html",
        {
            "request": request,
            "application": application,
            "event": event,
            "messages": messages,
            "user": user,
        },
    )


@router.post("/{application_id}")
def post_message(
    request: Request,
    application_id: int,
    content: str = Form(...),
    session: Session = Depends(session_dependency),
    user=Depends(get_current_user),
):
    application = _load_application(session, application_id)
    _authorize(session, user, application)
    try:
        send_message(session, application, user, content=content)
    except ValidationError as exc:
        messages = list_messages_for_application(session, application.id)
        return templates.TemplateResponse(
            "messages/thread.html",
            {"request": request, "messages": messages, "error": str(exc)},
            status_code=400,
        )
    messages = list_messages_for_application(session, application.id)
    return templates.TemplateResponse(
        "messages/thread.html",
        {"request": request, "messages": messages},
    )
