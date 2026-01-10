from sqlmodel import Session, select, col
from typing import Sequence
from ..models.service import Service, ServiceCreate, ServiceCategory
from ..models.user import User, Role
from ..models.reservation import Reservation, ReservationStatus
from ..core.exceptions import (
    ReservationNotFoundError,
    ServiceNotChosenError,
    ForbiddenActionError,
    ServiceNotFoundError,
)


def create_new_service(
    session: Session, user: User, service_input: ServiceCreate
) -> Service:
    target_coach = None
    target_coach_id = None

    if user.role == Role.ADMIN:
        if not service_input.coach_id:
            raise ValueError(
                "Coach ID must be provided by admin when creating a service."
            )

        found_coach = session.get(User, service_input.coach_id)

        if not found_coach or found_coach.role != Role.COACH:
            raise ServiceNotFoundError()

        target_coach_id = found_coach.id
        target_coach = found_coach
    else:
        target_coach_id = user.id
        target_coach = user

    service = Service.model_validate(service_input)
    service.coach_id = target_coach_id
    service.requires_coach = True
    service.coach = target_coach

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

    statement = select(Reservation).where(
        Reservation.service_id.in_(coach_services_ids)
    )
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


def select_available_services(
    session: Session, name: str | None = None, category: ServiceCategory | None = None
) -> Sequence[Service]:
    statement = select(Service).where(Service.is_available == True)

    if name:
        statement = statement.where(col(Service.name).ilike(f"%{name}%"))

    if category:
        statement = statement.where(Service.category == category)

    return session.exec(statement).all()


def remove_service(service_id: int, current_user: User, session: Session):
    service = session.get(Service, service_id)
    if not service:
        raise ServiceNotFoundError()

    session.delete(service)
    session.commit()
    return {"msg": "Service deleted successfully"}
