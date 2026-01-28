from fastapi import Depends, HTTPException, Request
from sqlmodel import Session

from app.db import get_session
from app.repositories.user_repo import get_user


def session_dependency() -> Session:
    session = get_session()
    try:
        yield session
    finally:
        session.close()


def get_current_user(
    request: Request, session: Session = Depends(session_dependency)
):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="login_required")
    user = get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="user_not_found")
    return user


def require_role(required_role: str):
    def _checker(user=Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(status_code=403, detail="forbidden")
        return user

    return _checker
