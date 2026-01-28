from sqlmodel import Session, select

from app.models import Review


def find_review(
    session: Session, application_id: int, author_id: int
) -> Review | None:
    statement = select(Review).where(
        Review.application_id == application_id,
        Review.author_id == author_id,
    )
    return session.exec(statement).first()


def save_review(session: Session, review: Review) -> Review:
    session.add(review)
    session.commit()
    session.refresh(review)
    return review
