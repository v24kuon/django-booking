import os

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.errors import ValidationError
from app.models import User
from app.routes.deps import session_dependency
from app.services.auth_service import register_user

router = APIRouter(prefix="/setup", tags=["setup"])
templates = Jinja2Templates(directory="app/templates")


def _get_setup_token() -> str | None:
    return os.environ.get("ADMIN_SETUP_TOKEN")


def _ensure_setup_enabled() -> str:
    token = _get_setup_token()
    if not token:
        raise HTTPException(status_code=404, detail="not_found")
    return token


def _admin_exists(session: Session) -> bool:
    statement = select(User).where(User.role == "admin")
    return session.exec(statement).first() is not None


@router.get("/admin")
def admin_setup_page(
    request: Request, session: Session = Depends(session_dependency)
):
    _ensure_setup_enabled()
    already_setup = _admin_exists(session)
    return templates.TemplateResponse(
        "setup/admin_create.html",
        {
            "request": request,
            "already_setup": already_setup,
        },
    )


@router.post("/admin")
def admin_setup_create(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    setup_token: str = Form(...),
    session: Session = Depends(session_dependency),
):
    token = _ensure_setup_enabled()
    if _admin_exists(session):
        return templates.TemplateResponse(
            "setup/admin_create.html",
            {
                "request": request,
                "already_setup": True,
                "error": "既に管理者アカウントが作成されています。",
            },
            status_code=400,
        )

    if setup_token != token:
        return templates.TemplateResponse(
            "setup/admin_create.html",
            {
                "request": request,
                "already_setup": False,
                "error": "セットアップトークンが正しくありません。",
            },
            status_code=400,
        )

    try:
        user = register_user(
            session, email=email, password=password, role="admin", allow_admin=True
        )
    except ValidationError as exc:
        return templates.TemplateResponse(
            "setup/admin_create.html",
            {
                "request": request,
                "already_setup": False,
                "error": str(exc),
                "email": email,
            },
            status_code=400,
        )

    request.session["user_id"] = user.id
    request.session["role"] = user.role
    return RedirectResponse(url="/admin", status_code=303)
