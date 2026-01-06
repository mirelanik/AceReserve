from sqlmodel import Session, select
from ..models.user import User, UserCoachFavorite, Role
from ..models.court import Court
from ..core.exceptions import (
    CourtNotFoundError,
    FavoriteAlreadyExistsError,
    CoachNotFoundError,
)


def add_court_to_favorites(session: Session, user: User, court_number: int):
    court = session.exec(select(Court).where(Court.number == court_number)).first()
    if not court:
        raise CourtNotFoundError()

    if court in user.favorite_courts:
        raise FavoriteAlreadyExistsError()

    user.favorite_courts.append(court)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": f"Court {court_number} added to favorites."}


def remove_court_from_favorites(session: Session, user: User, court_number: int):
    court = session.exec(select(Court).where(Court.number == court_number)).first()
    if court and court in user.favorite_courts:
        user.favorite_courts.remove(court)
        session.add(user)
        session.commit()
        session.refresh(user)
    return {"message": f"Court {court_number} removed from favorites."}


def list_favorite_courts(session: Session, user: User):
    return user.favorite_courts


def add_coach_to_favorites(session: Session, user: User, coach_id: int):
    coach = session.get(User, coach_id)
    if not coach or coach.role != Role.COACH:
        raise CoachNotFoundError()

    if coach in user.favorite_coaches:
        raise FavoriteAlreadyExistsError()

    user.favorite_coaches.append(coach)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": f"Coach {coach_id} added to favorites."}


def remove_coach_from_favorites(session: Session, user: User, coach_id: int):
    coach = session.get(User, coach_id)
    if coach and coach in user.favorite_coaches:
        user.favorite_coaches.remove(coach)
        session.add(user)
        session.commit()
        session.refresh(user)
    return {"message": f"Coach {coach_id} removed from favorites."}


def list_favorite_coaches(session: Session, user: User):
    return user.favorite_coaches
