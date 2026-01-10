from typing import Sequence
from datetime import datetime, timedelta
from sqlmodel import Session, select, col
from ..models.court import CourtCreate, Court
from ..core.exceptions import ExistingCourtError, CourtNotFoundError
from ..models.reservation import Reservation, ReservationStatus
from ..models.user import User


def create_court(
    session: Session, court_input: CourtCreate, current_user: User
) -> Court:
    existing_court = session.exec(
        select(Court).where(Court.number == court_input.number)
    ).first()

    if existing_court:
        raise ExistingCourtError()

    new_court = Court.model_validate(court_input)

    session.add(new_court)
    session.commit()
    session.refresh(new_court)

    return new_court


def remove_court(session: Session, court_number: int, current_user: User):
    court = session.get(Court, court_number)
    if not court:
        raise CourtNotFoundError()

    session.delete(court)
    session.commit()
    return {"msg": f"Court number {court_number} deleted successfully"}


def show_all_courts(session: Session) -> Sequence[Court]:
    return session.exec(select(Court)).all()


def show_court_by_number(session: Session, court_number: int) -> Court:
    court = session.exec(select(Court).where(Court.number == court_number)).first()
    if not court:
        raise CourtNotFoundError()

    return court


def select_courts_by_category(
    session: Session,
    surface: str | None = None,
    lighting: bool | None = None,
    start_datetime: datetime | None = None,
    duration: int = 60,
) -> Sequence[Court]:
    statement = select(Court).where(Court.available is True)

    if surface:
        statement = statement.where(col(Court.surface).ilike(f"%{surface}"))

    if lighting is not None:
        statement = statement.where(Court.has_lighting is True)

    if start_datetime:
        end_datetime = start_datetime + timedelta(minutes=duration)
        busy_courts_statement = select(Reservation.court_number).where(
            Reservation.status != ReservationStatus.CANCELLED,
            Reservation.start_time < end_datetime,
            Reservation.end_time > start_datetime,
        )
        busy_court_ids = session.exec(busy_courts_statement).all()

        if busy_court_ids:
            statement = statement.where(col(Court.number).not_in(busy_court_ids))

    return session.exec(statement).all()
