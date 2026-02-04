import logging
import os
from pathlib import Path

from sqlmodel import SQLModel, Session, create_engine

# プロジェクトルートのパスを取得
BASE_DIR = Path(__file__).parent.parent

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
        DATABASE_URL = "sqlite:////tmp/app.db"
    else:
        DATABASE_URL = f"sqlite:///{BASE_DIR / 'app.db'}"

DATABASE_PATH = None
if DATABASE_URL.startswith("sqlite:///"):
    DATABASE_PATH = Path(DATABASE_URL.replace("sqlite:///", ""))

logger = logging.getLogger(__name__)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)


def init_db() -> None:
    try:
        if DATABASE_PATH:
            logger.info(f"Creating database at: {DATABASE_PATH}")
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database: {e}", exc_info=True)
        raise


def get_session() -> Session:
    return Session(engine)
