from sqlmodel import Session, select
from typing import Sequence
from ..models.court import CourtCreate, Court
from ..core.exceptions import ExistingCourtError, CourtNotFoundError


def create_court(session: Session, court_input: CourtCreate) -> Court:
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


def get_all_courts(session: Session) -> Sequence[Court]:
    return session.exec(select(Court)).all()


def get_court_by_number(session: Session, court_number: int) -> Court:
    court = session.exec(select(Court).where(Court.number == court_number)).first()
    if not court:
        raise CourtNotFoundError()

    return court
