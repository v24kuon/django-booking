from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Timestamped(SQLModel):
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class User(Timestamped, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False)
    hashed_password: str
    role: str = Field(index=True)
    is_active: bool = Field(default=True)
    last_login_at: Optional[datetime] = None

    __table_args__ = (UniqueConstraint("email", name="uq_user_email"),)


class StallholderProfile(Timestamped, table=True):
    __tablename__ = "stallholder_profile"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    business_name: str
    genre: str
    bio: str
    profile_image: Optional[str] = None
    past_achievements: Optional[str] = None
    website_url: Optional[str] = None
    review_status: str = Field(default="pending")
    reviewed_by: Optional[int] = Field(default=None, foreign_key="user.id")
    reviewed_at: Optional[datetime] = None
    review_note: Optional[str] = None

    __table_args__ = (UniqueConstraint("user_id", name="uq_stallholder_profile_user"),)


class OrganizerProfile(Timestamped, table=True):
    __tablename__ = "organizer_profile"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    organization_name: str
    description: str
    profile_image: Optional[str] = None
    location: Optional[str] = None

    __table_args__ = (UniqueConstraint("user_id", name="uq_organizer_profile_user"),)


class Event(Timestamped, table=True):
    __tablename__ = "event"

    id: Optional[int] = Field(default=None, primary_key=True)
    organizer_id: int = Field(foreign_key="user.id", index=True)
    title: str
    description: str
    region: str = Field(index=True)
    venue_address: str
    genre: str = Field(index=True)
    start_date: datetime
    end_date: datetime
    application_deadline: datetime
    capacity: int
    status: str = Field(default="draft", index=True)

    __table_args__ = (
        Index(
            "ix_event_search",
            "region",
            "genre",
            "start_date",
            "application_deadline",
            "status",
        ),
    )


class Application(Timestamped, table=True):
    __tablename__ = "application"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id", index=True)
    stallholder_id: int = Field(foreign_key="user.id", index=True)
    memo: Optional[str] = None
    status: str = Field(default="pending", index=True)
    decided_at: Optional[datetime] = None

    __table_args__ = (
        UniqueConstraint(
            "event_id",
            "stallholder_id",
            name="uq_application_event_stallholder",
        ),
        Index(
            "ix_application_event_status_created",
            "event_id",
            "stallholder_id",
            "status",
            "created_at",
        ),
    )


class Message(SQLModel, table=True):
    __tablename__ = "message"

    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id", index=True)
    sender_id: int = Field(foreign_key="user.id")
    content: str
    is_read: bool = Field(default=False, index=True)
    read_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utc_now)

    __table_args__ = (Index("ix_message_application_created", "application_id", "created_at"),)


class Review(SQLModel, table=True):
    __tablename__ = "review"

    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id", index=True)
    author_id: int = Field(foreign_key="user.id")
    target_id: int = Field(foreign_key="user.id")
    score: int
    comment: str
    is_hidden: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now)

    __table_args__ = (
        UniqueConstraint(
            "application_id",
            "author_id",
            name="uq_review_application_author",
        ),
    )


class Report(Timestamped, table=True):
    __tablename__ = "report"

    id: Optional[int] = Field(default=None, primary_key=True)
    reporter_id: int = Field(foreign_key="user.id")
    target_type: str
    target_id: int
    reason_code: Optional[str] = None
    reason_detail: Optional[str] = None
    status: str = Field(default="open", index=True)
    handled_by: Optional[int] = Field(default=None, foreign_key="user.id")
    handled_at: Optional[datetime] = None
    resolution_note: Optional[str] = None

    __table_args__ = (
        Index("ix_report_status_created", "status", "created_at"),
        Index("ix_report_target", "target_type", "target_id"),
    )


class AdminNote(Timestamped, table=True):
    __tablename__ = "admin_note"

    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="user.id")
    target_type: str
    target_id: int
    note: str


class Guide(Timestamped, table=True):
    __tablename__ = "guide"

    id: Optional[int] = Field(default=None, primary_key=True)
    target_role: str
    title: str
    body: str
    is_published: bool = Field(default=False, index=True)
    published_at: Optional[datetime] = None

    __table_args__ = (Index("ix_guide_target_published", "target_role", "is_published", "published_at"),)


class Notification(SQLModel, table=True):
    __tablename__ = "notification"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    event_type: str
    channel: str
    title: str
    body: str
    related_type: Optional[str] = None
    related_id: Optional[int] = None
    delivery_status: str = Field(default="queued", index=True)
    is_read: bool = Field(default=False, index=True)
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utc_now)

    __table_args__ = (
        Index(
            "ix_notification_user_status_created",
            "user_id",
            "is_read",
            "created_at",
            "delivery_status",
        ),
    )
