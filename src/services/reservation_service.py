from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select
from typing import Sequence
from ..core.exceptions import StartTimeError, DoubleBookingError, CourtNotFoundError, ReservationNotFoundError, ForbiddenActionError
from ..models.reservation import Reservation, ReservationStatus, ReservationCreate
from ..models.user import User, Role
from ..models.court import Court
from .loyalty_service import (
    calculate_price,
    calculate_earned_points,
    update_loyalty_level,
)


def _validate_availability(
    session: Session, court_number: int, start_time: datetime, end_time: datetime
) -> bool:
    if start_time < datetime.now(timezone.utc):
        raise StartTimeError()

    statement = select(Reservation).where(
        Reservation.court_number == court_number,
        Reservation.status != ReservationStatus.CANCELLED,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time,
    )

    conflict = session.exec(statement).first()

    if conflict:
        raise DoubleBookingError()

    return True


def process_reservation_creation(
    session: Session, user: User, data: ReservationCreate
) -> Reservation:
    end_time = data.start_time + timedelta(minutes=data.duration_minutes)

    _validate_availability(session, data.court_number, data.start_time, end_time)

    court = session.get(Court, data.court_number)
    if not court:
        raise CourtNotFoundError()

    total_price = calculate_price(court, data.duration_minutes, user)

    reservation = Reservation(
        court_number=data.court_number,
        user_id=user.id,
        start_time=data.start_time,
        end_time=end_time,
        duration_minutes=data.duration_minutes,
        status=ReservationStatus.CONFIRMED,
        total_price=total_price,
    )

    session.add(reservation)

    if user.loyalty:
        points_earned = calculate_earned_points(data.duration_minutes)
        update_loyalty_level(user, user.loyalty, points_earned)
        session.add(user.loyalty)

    session.commit()
    session.refresh(reservation)

    return reservation

def get_user_reservations(session: Session, user:User) -> Sequence[Reservation]:
    reservations = select(Reservation).where(Reservation.user_id == user.id)
    return session.exec(reservations).all()

def delete_reservation(session: Session, user: User, reservation_id: int) -> dict:
    reservation = session.get(Reservation, reservation_id)
    if not reservation: 
        raise ReservationNotFoundError()
    
    if reservation.user_id != user.id or user.role != Role.ADMIN:
        raise ForbiddenActionError()
    
    reservation.status = ReservationStatus.CANCELLED
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    
    return {"message": "Reservation was cancelled successfully."}