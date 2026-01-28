import os
import secrets

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from app.db import init_db
from app.routes import admin, auth, organizer, stallholder
from app.routes import messages
from app.routes import notifications


def create_app() -> FastAPI:
    app = FastAPI()
    secret_key = os.environ.get("SESSION_SECRET") or secrets.token_hex(32)
    app.add_middleware(SessionMiddleware, secret_key=secret_key)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    app.include_router(auth.router)
    app.include_router(stallholder.router, prefix="/stallholder")
    app.include_router(organizer.router, prefix="/organizer")
    app.include_router(admin.router, prefix="/admin")
    app.include_router(messages.router)
    app.include_router(notifications.router)

    return app


app = create_app()
