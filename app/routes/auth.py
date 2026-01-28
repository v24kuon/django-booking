from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.errors import AuthenticationError, ValidationError
from app.models import Event, User
from app.repositories.user_repo import get_user
from app.routes.deps import session_dependency
from app.services.auth_service import authenticate_user, register_user
from app.utils import (
    APPLICATION_STATUS_LABELS,
    EVENT_STATUS_LABELS,
    PROFILE_REVIEW_STATUS_LABELS,
    REPORT_STATUS_LABELS,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# グローバル変数として辞書を追加
templates.env.globals["event_status_labels"] = EVENT_STATUS_LABELS
templates.env.globals["app_status_labels"] = APPLICATION_STATUS_LABELS
templates.env.globals["report_status_labels"] = REPORT_STATUS_LABELS
templates.env.globals["profile_review_status_labels"] = PROFILE_REVIEW_STATUS_LABELS


def get_user_from_session(request: Request, session: Session) -> User | None:
    """セッションからユーザー情報を取得（オプショナル）"""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return get_user(session, user_id)


@router.get("/")
def index(request: Request, session: Session = Depends(session_dependency)):
    # 募集中のイベントを取得
    events = list(session.exec(select(Event).where(Event.status == "open")).all())
    # ユーザー情報を取得（ログイン済みの場合）
    user = get_user_from_session(request, session)
    return templates.TemplateResponse("auth/index.html", {"request": request, "events": events, "user": user})


@router.get("/register")
def register_page(request: Request, session: Session = Depends(session_dependency)):
    # ログイン済みの場合は適切なダッシュボードにリダイレクト
    user = get_user_from_session(request, session)
    if user:
        if user.role == "admin":
            return RedirectResponse(url="/admin", status_code=303)
        elif user.role == "stallholder":
            return RedirectResponse(url="/stallholder", status_code=303)
        elif user.role == "organizer":
            return RedirectResponse(url="/organizer", status_code=303)
    return templates.TemplateResponse("auth/register.html", {"request": request, "user": user})


@router.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    session: Session = Depends(session_dependency),
):
    try:
        user = register_user(session, email=email, password=password, role=role)
    except ValidationError as exc:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": str(exc), "email": email},
            status_code=400,
        )

    request.session["user_id"] = user.id
    request.session["role"] = user.role
    return RedirectResponse(url="/stallholder" if user.role == "stallholder" else "/organizer", status_code=303)


@router.get("/login")
def login_page(request: Request, session: Session = Depends(session_dependency)):
    # ログイン済みの場合は適切なダッシュボードにリダイレクト
    user = get_user_from_session(request, session)
    if user:
        if user.role == "admin":
            return RedirectResponse(url="/admin", status_code=303)
        elif user.role == "stallholder":
            return RedirectResponse(url="/stallholder", status_code=303)
        elif user.role == "organizer":
            return RedirectResponse(url="/organizer", status_code=303)
    return templates.TemplateResponse("auth/login.html", {"request": request, "user": user})


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(session_dependency),
):
    try:
        user = authenticate_user(session, email=email, password=password)
    except AuthenticationError as exc:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": str(exc), "email": email},
            status_code=400,
        )

    request.session["user_id"] = user.id
    request.session["role"] = user.role
    if user.role == "admin":
        return RedirectResponse(url="/admin", status_code=303)
    if user.role == "stallholder":
        return RedirectResponse(url="/stallholder", status_code=303)
    return RedirectResponse(url="/organizer", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
