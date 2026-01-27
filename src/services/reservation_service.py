"""Reservation management service functions.
Handles court reservation creation, modification, cancellation, and validation
including availability checking and pricing calculations.
"""

from typing import Sequence
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
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
)

LIGHTING_START_HOUR = 19


class ReservationService:
    """Service for managing tennis court reservations.
    Handles all reservation operations including creation, modification,
    cancellation, and comprehensive validation of court/coach availability,
    lighting requirements, and pricing calculations.
    """

    def __init__(self, session: AsyncSession):
        """Initialize ReservationService with database session.
        Args:
            session: Async SQLAlchemy database session.
        """
        self.session = session

    async def _validate_court_availability(
        self,
        court_number: int,
        start_time: datetime,
        end_time: datetime,
        exclude_reservation_id: int | None = None,
    ) -> None:
        """Check that court is not already booked during requested time.
        Args:
            court_number: The court to check.
            start_time: Reservation start time.
            end_time: Reservation end time.
            exclude_reservation_id: Reservation ID to exclude from check (for updates).
        Raises:
            StartTimeError: If start time is in the past.
            DoubleCourtBookingError: If court is already booked.
        """
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

        result = await self.session.execute(statement)
        conflict = result.scalars().first()

        if conflict:
            raise DoubleCourtBookingError()

    async def _validate_coach_availability(
        self,
        coach_id: int | None,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        """Check that coach is not already booked during requested time.
        Args:
            coach_id: The coach to check (None skips validation).
            start_time: Service start time.
            end_time: Service end time.
        Raises:
            DoubleCoachBookingError: If coach is already booked.
        """
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

        result = await self.session.execute(statement)
        conflict = result.scalars().first()

        if conflict:
            raise DoubleCoachBookingError()

    def _validate_lighting_requirements(
        self, court: Court, start_time: datetime, wants_lighting: bool
    ) -> None:
        """Validate that court supports lighting and time is appropriate.
        Args:
            court: The court for the reservation.
            start_time: Reservation start time.
            wants_lighting: Whether lighting is requested.
        Raises:
            LightingAvailabilityError: If court doesn't have lighting.
            LightingTimeError: If lighting is requested before allowed hour.
        """
        if not wants_lighting:
            return

        if not court.has_lighting:
            raise LightingAvailabilityError()

        if start_time.hour < LIGHTING_START_HOUR:
            raise LightingTimeError()

    async def _validate_service(
        self,
        service_id: int | None,
        start_time: datetime,
        end_time: datetime,
    ) -> Service | None:
        """Validate that service exists and coach (if required) is available.
        Args:
            service_id: ID of the service (None skips validation).
            start_time: Service start time.
            end_time: Service end time.
        Returns:
            Service | None: The service if valid, None if not requested.
        Raises:
            ServiceNotFoundError: If service doesn't exist.
            DoubleCoachBookingError: If coach is already booked.
        """
        if not service_id:
            return None
        service = await self.session.get(Service, service_id)
        if not service:
            raise ServiceNotFoundError()

        if service.requires_coach:
            await self._validate_coach_availability(
                service.coach_id, start_time, end_time
            )

        return service

    def _calculate_end_time(
        self, start_time: datetime, duration_minutes: int
    ) -> datetime:
        """Calculate reservation end time from start time and duration.
        Args:
            start_time: The start time.
            duration_minutes: Duration in minutes.
        Returns:
            datetime: The calculated end time.
        """
        end_time = start_time + timedelta(minutes=duration_minutes)
        return end_time

    async def _update_user_loyalty(self, user: User, duration_minutes: int) -> None:
        """Award loyalty points for a completed reservation.
        Args:
            user: The user making the reservation.
            duration_minutes: Reservation duration in minutes.
        """
        if not user.loyalty:
            return

        points_earned = calculate_earned_points(duration_minutes)
        update_loyalty_level(user.loyalty, points_earned)
        self.session.add(user.loyalty)

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
        Raises:
            CourtNotFoundError: If court doesn't exist.
            StartTimeError: If start time is in the past.
            DoubleCourtBookingError: If court is already booked.
            LightingAvailabilityError: If lighting not available.
            LightingTimeError: If lighting requested outside allowed hours.
            ServiceNotFoundError: If service doesn't exist.
            DoubleCoachBookingError: If coach is already booked.
        """
        end_time = self._calculate_end_time(data.start_time, data.duration_minutes)

        court_result = await self.session.execute(
            select(Court).where(Court.number == data.court_number)
        )
        court = court_result.scalars().first()
        if not court:
            raise CourtNotFoundError()

        await self._validate_court_availability(
            data.court_number, data.start_time, end_time
        )

        self._validate_lighting_requirements(
            court, data.start_time, data.wants_lighting
        )

        await self._validate_service(data.service_id, data.start_time, end_time)

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

        self.session.add(reservation)

        await self._update_user_loyalty(user, data.duration_minutes)

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
        Raises:
            ReservationNotFoundError: If reservation doesn't exist.
            ForbiddenActionError: If user doesn't own the reservation (and isn't admin).
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
        Raises:
            ReservationNotFoundError: If reservation doesn't exist.
            ForbiddenActionError: If user doesn't own the reservation (and isn't admin).
            DoubleCourtBookingError: If new court/time is already booked.
            CourtNotFoundError: If new court doesn't exist.
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
        new_end_time = self._calculate_end_time(new_start_time, new_duration)

        time_changed = (new_start_time != reservation.start_time) or (
            new_duration != reservation.duration_minutes
        )
        court_changed = new_court_number != reservation.court_number

        if time_changed or court_changed:
            await self._validate_court_availability(
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

        new_price = calculate_price(court, temp_create_data, user)
        reservation.total_price = new_price

        self.session.add(reservation)
        await self.session.commit()
        await self.session.refresh(reservation)

        return reservation
