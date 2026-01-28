from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.models import Notification
from app.repositories.notification_repo import list_notifications_for_user
from app.routes.deps import get_current_user, session_dependency
from app.services.notification_service import mark_notification_read

router = APIRouter(prefix="/notifications", tags=["notifications"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def notifications_list(
    request: Request,
    session: Session = Depends(session_dependency),
    user=Depends(get_current_user),
):
    notifications = list_notifications_for_user(session, user.id)
    return templates.TemplateResponse(
        "notifications/index.html",
        {"request": request, "notifications": notifications, "user": user},
    )


@router.post("/{notification_id}/read")
def mark_read(
    notification_id: int,
    session: Session = Depends(session_dependency),
    user=Depends(get_current_user),
):
    notification = session.get(Notification, notification_id)
    if not notification or notification.user_id != user.id:
        raise HTTPException(status_code=404, detail="notification_not_found")
    mark_notification_read(session, notification)
    return RedirectResponse(url="/notifications", status_code=303)
