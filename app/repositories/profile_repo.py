from sqlmodel import Session, select

from app.models import OrganizerProfile, StallholderProfile


def get_stallholder_profile(session: Session, user_id: int) -> StallholderProfile | None:
    statement = select(StallholderProfile).where(StallholderProfile.user_id == user_id)
    return session.exec(statement).first()


def get_organizer_profile(session: Session, user_id: int) -> OrganizerProfile | None:
    statement = select(OrganizerProfile).where(OrganizerProfile.user_id == user_id)
    return session.exec(statement).first()


def save_stallholder_profile(
    session: Session, profile: StallholderProfile
) -> StallholderProfile:
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def save_organizer_profile(
    session: Session, profile: OrganizerProfile
) -> OrganizerProfile:
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile
