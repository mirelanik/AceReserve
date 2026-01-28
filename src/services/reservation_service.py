"""Reservation management service functions.
Handles court reservation creation, modification, cancellation, and validation
including availability checking and pricing calculations.
"""

from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from ..core.exceptions import (
    CourtNotFoundError,
    ReservationNotFoundError,
    ForbiddenActionError,
)
from ..models.reservation import (
    Reservation,
    ReservationStatus,
    ReservationCreate,
    ReservationUpdate,
)
from ..models.user import User, Role
from ..models.court import Court
from .pricing_service import PricingService
from .validation_helpers import ValidationHelpers

LIGHTING_START_HOUR = 19


class ReservationService:
    """Service for managing tennis court reservations.
    Handles all reservation operations including creation, modification and cancellation.
    """

    def __init__(self, session: AsyncSession):
        """Initialize ReservationService with database session.
        Args:
            session: Async SQLAlchemy database session.
        """
        self.session = session
        self.validator = ValidationHelpers(session)

    async def process_reservation_creation(
        self, user: User, data: ReservationCreate
    ) -> Reservation:
        """Create a new court reservation with full validation.
        Validates court and coach availability, checks lighting requirements,
        calculates price with loyalty discounts, and awards loyalty points.

        Args:
            user: The user making the reservation.
            data: Reservation creation data.
        Returns:
            Reservation: The newly created confirmed reservation.
        """
        end_time = self.validator.calculate_end_time(
            data.start_time, data.duration_minutes
        )

        court_result = await self.session.execute(
            select(Court).where(Court.number == data.court_number)
        )
        court = court_result.scalars().first()
        if not court:
            raise CourtNotFoundError()

        await self.validator.validate_court_availability(
            data.court_number, data.start_time, end_time
        )

        self.validator.validate_lighting_requirements(
            court, data.start_time, data.wants_lighting
        )

        await self.validator.validate_service(
            data.service_id, data.start_time, end_time
        )

        total_price = PricingService.calculate_price(court, data, user)

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

        self.session.add(reservation)

        await self.validator.update_user_loyalty(user, data.duration_minutes)

        await self.session.commit()
        await self.session.refresh(reservation)

        return reservation

    async def get_user_reservations(self, user: User) -> Sequence[Reservation]:
        """Get all reservations for a specific user.
        Args:
            user: The user to get reservations for.
        Returns:
            Sequence[Reservation]: All reservations belonging to the user.
        """
        reservations = select(Reservation).where(Reservation.user_id == user.id)
        result = await self.session.execute(reservations)
        return result.scalars().all()

    async def delete_reservation(self, user: User, reservation_id: int) -> dict:
        """Cancel a reservation.
        Args:
            user: The user requesting cancellation.
            reservation_id: ID of the reservation to cancel.
        Returns:
            dict: Success message.
        """
        reservation = await self.session.get(Reservation, reservation_id)
        if not reservation:
            raise ReservationNotFoundError()

        if reservation.user_id != user.id and user.role != Role.ADMIN:
            raise ForbiddenActionError()

        reservation.status = ReservationStatus.CANCELLED
        self.session.add(reservation)
        await self.session.commit()
        await self.session.refresh(reservation)

        return {"message": "Reservation was cancelled successfully."}

    async def modify_reservation(
        self,
        user: User,
        reservation_id: int,
        update_data: ReservationUpdate,
    ) -> Reservation:
        """Update reservation details (date, time, court, extras).
        Revalidates availability if court or time changed, recalculates price.

        Args:
            user: The user requesting the modification.
            reservation_id: ID of the reservation to modify.
            update_data: New values for reservation fields.
        Returns:
            Reservation: The updated reservation.
        """
        reservation = await self.session.get(Reservation, reservation_id)
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
        new_end_time = self.validator.calculate_end_time(new_start_time, new_duration)

        time_changed = (new_start_time != reservation.start_time) or (
            new_duration != reservation.duration_minutes
        )
        court_changed = new_court_number != reservation.court_number

        if time_changed or court_changed:
            await self.validator.validate_court_availability(
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

        court_result = await self.session.execute(
            select(Court).where(Court.number == new_court_number)
        )
        court = court_result.scalars().first()
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

        new_price = PricingService.calculate_price(court, temp_create_data, user)
        reservation.total_price = new_price

        self.session.add(reservation)
        await self.session.commit()
        await self.session.refresh(reservation)

        return reservation
