from datetime import datetime, timezone

from sqlmodel import Session

from app.errors import ValidationError
from app.models import Application, Review, User
from app.repositories.review_repo import find_review, save_review
from app.services.notification_service import create_notification


def create_review(
    session: Session,
    application: Application,
    author: User,
    target: User,
    score: int,
    comment: str,
) -> Review:
    if score < 1 or score > 5:
        raise ValidationError("score_invalid")

    existing = find_review(session, application.id, author.id)
    if existing:
        raise ValidationError("review_exists")

    review = Review(
        application_id=application.id,
        author_id=author.id,
        target_id=target.id,
        score=score,
        comment=comment,
        created_at=datetime.now(timezone.utc),
    )
    review = save_review(session, review)

    create_notification(
        session,
        target,
        event_type="review_posted",
        title="レビューが投稿されました",
        body=f"スコア: {score}/5 - {comment[:50]}",
        related_type="review",
        related_id=review.id,
    )

    if score <= 2:
        from app.models import Event

        event = session.get(Event, application.event_id)
        if event:
            organizer = session.get(User, event.organizer_id)
            if organizer:
                create_notification(
                    session,
                    organizer,
                    event_type="low_rating",
                    title="低評価レビューが投稿されました",
                    body=f"イベント「{event.title}」に低評価レビューが投稿されました。",
                    related_type="review",
                    related_id=review.id,
                )

    return review
