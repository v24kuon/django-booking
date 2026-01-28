from datetime import datetime, timezone

import pytest
from sqlmodel import SQLModel, Session, create_engine

import app.models  # noqa: F401


@pytest.fixture()
def session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture()
def now_utc() -> datetime:
    return datetime.now(timezone.utc)
