import logging
import os
import secrets
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from app.db import init_db
from app.routes import admin, auth, organizer, stallholder
from app.routes import messages
from app.routes import notifications

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# プロジェクトルートのパスを取得
BASE_DIR = Path(__file__).parent.parent


def create_app() -> FastAPI:
    app = FastAPI()
    secret_key = os.environ.get("SESSION_SECRET") or secrets.token_hex(32)
    app.add_middleware(SessionMiddleware, secret_key=secret_key)
    
    # 静的ファイルディレクトリが存在する場合のみマウント
    static_dir = BASE_DIR / "app" / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    else:
        logger.warning(f"Static directory not found: {static_dir}")

    @app.on_event("startup")
    def on_startup() -> None:
        try:
            logger.info("Initializing database...")
            init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise

    # エラーハンドリング
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "type": type(exc).__name__},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation error: {exc}")
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    app.include_router(auth.router)
    app.include_router(stallholder.router, prefix="/stallholder")
    app.include_router(organizer.router, prefix="/organizer")
    app.include_router(admin.router, prefix="/admin")
    app.include_router(messages.router)
    app.include_router(notifications.router)

    return app


app = create_app()
