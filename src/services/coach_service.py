from sqlmodel import Session, select
from typing import Sequence
from ..models.service import Service, ServiceCreate
from ..models.user import User
from ..models.reservation import Reservation, ReservationStatus
from ..core.exceptions import (
    ReservationNotFoundError,
    ServiceNotChosenError,
    ForbiddenActionError,
)


def create_new_service(
    session: Session, user: User, service_input: ServiceCreate
) -> Service:
    service = Service.model_validate(service_input)
    service.coach_id = user.id
    service.requires_coach = True

    session.add(service)
    session.commit()
    session.refresh(service)

    return service


def get_services_by_coach(session: Session, user: User) -> list[Service]:
    return user.services


def get_reservations_for_coach(session: Session, user: User) -> Sequence[Reservation]:
    coach_services_ids = [s.id for s in user.services if s.id is not None]

    if not coach_services_ids:
        return []

    statement = select(Reservation).where(Reservation.service_id.in_(coach_services_ids))
    reservations = session.exec(statement).all()

    return reservations


def process_reservation_confirmation(
    session: Session, user: User, reservation_id: int
) -> Reservation:
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise ReservationNotFoundError()

    service = session.get(Service, reservation.service_id)

    if not service:
        raise ServiceNotChosenError()

    if service.coach_id != user.id:
        raise ForbiddenActionError()

    reservation.status = ReservationStatus.CONFIRMED

    session.add(reservation)
    session.commit()
    session.refresh(reservation)

    return reservation


def get_all_available_services(session: Session) -> Sequence[Service]:
    statement = select(Service).where(Service.is_available == True)
    return session.exec(statement).all()
