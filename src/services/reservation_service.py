from typing import Sequence
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select
from ..core.exceptions import (
    StartTimeError,
    DoubleCourtBookingError,
    DoubleCoachBookingError,
    CourtNotFoundError,
    ReservationNotFoundError,
    ServiceNotFoundError,
    ForbiddenActionError,
    LightingAvailabilityError,
    LightingTimeError,
)
from ..models.reservation import (
    Reservation,
    ReservationStatus,
    ReservationCreate,
    ReservationUpdate,
)
from ..models.user import User, Role
from ..models.court import Court
from ..models.service import Service
from .loyalty_service import update_loyalty_level
from .pricing_service import (
    calculate_price,
    calculate_earned_points,
    LIGHTING_START_HOUR,
)


def _validate_court_availability(
    session: Session,
    court_number: int,
    start_time: datetime,
    end_time: datetime,
    exclude_reservation_id: int | None = None,
) -> None:
    if start_time < datetime.now(timezone.utc):
        raise StartTimeError()

    statement = select(Reservation).where(
        Reservation.court_number == court_number,
        Reservation.status != ReservationStatus.CANCELLED,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time,
    )

    if exclude_reservation_id is not None:
        statement = statement.where(Reservation.id != exclude_reservation_id)

    conflict = session.exec(statement).first()

    if conflict:
        raise DoubleCourtBookingError()


def _validate_coach_availability(
    session: Session, coach_id: int | None, start_time: datetime, end_time: datetime
) -> None:
    if coach_id is None:
        return

    statement = (
        select(Reservation)
        .join(Service)
        .where(
            Reservation.service_id == Service.id,
            Service.coach_id == coach_id,
            Reservation.status != ReservationStatus.CANCELLED,
            Reservation.start_time < end_time,
            Reservation.end_time > start_time,
        )
    )

    conflict = session.exec(statement).first()

    if conflict:
        raise DoubleCoachBookingError()


def _validate_lighting_requirements(
    court: Court, start_time: datetime, wants_lighting: bool
) -> None:
    if not wants_lighting:
        return

    if not court.has_lighting:
        raise LightingAvailabilityError()

    if start_time.hour < LIGHTING_START_HOUR:
        raise LightingTimeError()


def _validate_service(
    session: Session, service_id: int | None, start_time: datetime, end_time: datetime
) -> Service | None:
    if not service_id:
        return None

    service = session.get(Service, service_id)
    if not service:
        raise ServiceNotFoundError()

    if service.requires_coach:
        _validate_coach_availability(session, service.coach_id, start_time, end_time)

    return service


def _calculate_end_time(start_time: datetime, duration_minutes: int) -> datetime:
    end_time = start_time + timedelta(minutes=duration_minutes)
    return end_time


def _update_user_loyalty(session: Session, user: User, duration_minutes: int) -> None:
    if not user.loyalty:
        return

    points_earned = calculate_earned_points(duration_minutes)
    update_loyalty_level(user.loyalty, points_earned)
    session.add(user.loyalty)


def process_reservation_creation(
    session: Session, user: User, data: ReservationCreate
) -> Reservation:
    end_time = _calculate_end_time(data.start_time, data.duration_minutes)

    court = session.exec(select(Court).where(Court.number == data.court_number)).first()
    if not court:
        raise CourtNotFoundError()

    _validate_court_availability(session, data.court_number, data.start_time, end_time)

    _validate_lighting_requirements(court, data.start_time, data.wants_lighting)

    _validate_service(session, data.service_id, data.start_time, end_time)

    total_price = calculate_price(court, data, user)

    reservation = Reservation(
        court_number=data.court_number,
        user_id=user.id,
        start_time=data.start_time,
        end_time=end_time,
        duration_minutes=data.duration_minutes,
        status=ReservationStatus.CONFIRMED,
        total_price=total_price,
        service_id=data.service_id,
        rent_racket=data.rent_racket,
        rent_balls=data.rent_balls,
        notes=data.notes,
    )

    session.add(reservation)

    _update_user_loyalty(session, user, data.duration_minutes)

    session.commit()
    session.refresh(reservation)

    return reservation


def get_user_reservations(session: Session, user: User) -> Sequence[Reservation]:
    reservations = select(Reservation).where(Reservation.user_id == user.id)
    return session.exec(reservations).all()


def delete_reservation(session: Session, user: User, reservation_id: int) -> dict:
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise ReservationNotFoundError()

    if reservation.user_id != user.id and user.role != Role.ADMIN:
        raise ForbiddenActionError()

    reservation.status = ReservationStatus.CANCELLED
    session.add(reservation)
    session.commit()
    session.refresh(reservation)

    return {"message": "Reservation was cancelled successfully."}


def modify_reservation(
    session: Session, user: User, reservation_id: int, update_data: ReservationUpdate
) -> Reservation:
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise ReservationNotFoundError()

    if reservation.user_id != user.id and user.role != Role.ADMIN:
        raise PermissionError()

    new_court_number = (
        update_data.court_number
        if update_data.court_number is not None
        else reservation.court_number
    )
    new_start_time = update_data.start_time or reservation.start_time
    new_duration = update_data.duration_minutes or reservation.duration_minutes
    new_end_time = _calculate_end_time(new_start_time, new_duration)

    time_changed = (new_start_time != reservation.start_time) or (
        new_duration != reservation.duration_minutes
    )
    court_changed = new_court_number != reservation.court_number

    if time_changed or court_changed:
        _validate_court_availability(
            session,
            new_court_number,
            new_start_time,
            new_end_time,
            exclude_reservation_id=reservation_id,
        )

    reservation.court_number = new_court_number
    reservation.start_time = new_start_time
    reservation.end_time = new_end_time
    reservation.duration_minutes = new_duration

    if update_data.rent_racket is not None:
        reservation.rent_racket = update_data.rent_racket
    if update_data.rent_balls is not None:
        reservation.rent_balls = update_data.rent_balls
    if update_data.wants_lighting is not None:
        reservation.wants_lighting = update_data.wants_lighting
    if update_data.notes is not None:
        reservation.notes = update_data.notes

    court = session.exec(select(Court).where(Court.number == new_court_number)).first()
    if not court:
        raise CourtNotFoundError()

    temp_create_data = ReservationCreate(
        court_number=reservation.court_number,
        start_time=reservation.start_time,
        duration_minutes=reservation.duration_minutes,
        rent_racket=reservation.rent_racket,
        rent_balls=reservation.rent_balls,
        wants_lighting=reservation.wants_lighting,
        service_id=reservation.service_id,
    )

    new_price = calculate_price(court, temp_create_data, user)
    reservation.total_price = new_price

    session.add(reservation)
    session.commit()
    session.refresh(reservation)

    return reservation
