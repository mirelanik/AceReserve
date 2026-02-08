"""Helper methods for validating reservations."""

from datetime import datetime, timedelta, timezone, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from ..core.exceptions import (
    StartTimeError,
    DoubleCourtBookingError,
    DoubleCoachBookingError,
    ServiceNotFoundError,
    LightingAvailabilityError,
    LightingTimeError,
    ClubNotOpenError,
    ClubClosedError,
    ForbiddenActionError,
)
from ..models.reservation import (
    Reservation,
    ReservationStatus,
)
from ..models.user import User
from ..models.court import Court
from ..models.service import Service
from ..models.loyalty import LoyaltyAccount
from .loyalty_service import LoyaltyService
from .pricing_service import PricingService

LIGHTING_START_HOUR = 19
CLUB_OPEN_TIME = time(8, 0)
CLUB_CLOSE_TIME = time(22, 0)


class ValidationHelpers:
    """Helper class for validating reservations and services."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def validate_court_availability(
        self,
        court_number: int,
        start_time: datetime,
        end_time: datetime,
        exclude_reservation_id: int | None = None,
    ) -> None:
        """Check that court is not already booked during requested time."""

        if start_time < datetime.now(timezone.utc):
            raise StartTimeError()
        statement = select(Reservation).where(
            Reservation.court_number == court_number,
            Reservation.status != ReservationStatus.CANCELLED,
            Reservation.start_time < end_time,
            Reservation.end_time > start_time,  # type: ignore
        )

        if exclude_reservation_id is not None:
            statement = statement.where(Reservation.id != exclude_reservation_id)

        result = await self.session.execute(statement)
        conflict = result.scalars().first()

        if conflict:
            raise DoubleCourtBookingError()

    async def validate_coach_availability(
        self,
        coach_id: int | None,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        """Check that coach is not already booked during requested time."""

        if coach_id is None:
            return
        statement = (
            select(Reservation)
            .join(Service)
            .where(
                Service.coach_id == coach_id,
                Reservation.status != ReservationStatus.CANCELLED,
                Reservation.start_time < end_time,  # type: ignore
                Reservation.end_time > start_time,  # type: ignore
            )
        )

        result = await self.session.execute(statement)
        conflict = result.scalars().first()

        if conflict:
            raise DoubleCoachBookingError()

    def validate_lighting_requirements(
        self, court: Court, start_time: datetime, wants_lighting: bool
    ) -> None:
        """Validate that court supports lighting and time is appropriate."""
        if not wants_lighting:
            return

        if not court.has_lighting:
            raise LightingAvailabilityError()

        if start_time.hour < LIGHTING_START_HOUR:
            raise LightingTimeError()

    async def validate_service(
        self,
        service_id: int | None,
        start_time: datetime,
        end_time: datetime,
    ) -> Service | None:
        """Validate that service exists and coach (if required) is available."""

        if not service_id:
            return None
        service = await self.session.get(Service, service_id)
        if not service:
            raise ServiceNotFoundError()

        if service.requires_coach:
            await self.validate_coach_availability(
                service.coach_id, start_time, end_time
            )

        return service

    def calculate_end_time(
        self, start_time: datetime, duration_minutes: int
    ) -> datetime:
        """Calculate reservation end time from start time and duration."""
        end_time = start_time + timedelta(minutes=duration_minutes)
        return end_time

    async def update_user_loyalty(self, user: User, duration_minutes: int) -> None:
        """Award loyalty points for a completed reservation."""

        statement = select(LoyaltyAccount).where(LoyaltyAccount.user_id == user.id)
        result = await self.session.execute(statement)
        loyalty = result.scalars().first()

        if not loyalty:
            return

        points_earned = PricingService.calculate_earned_points(duration_minutes)
        LoyaltyService.update_loyalty_level(loyalty, points_earned)
        self.session.add(loyalty)
        await self.session.flush()

    async def validate_operating_hours(
        self, start_time: datetime, end_time: datetime
    ) -> None:
        """Validate that reservation times are within club operating hours."""
        start = start_time.time()
        end = end_time.time()

        if start < CLUB_OPEN_TIME:
            raise ClubNotOpenError(f"Club opens at {CLUB_OPEN_TIME.strftime('%H:%M')}")

        if start >= CLUB_CLOSE_TIME:
            raise ClubClosedError(f"Club closes at {CLUB_CLOSE_TIME.strftime('%H:%M')}")

        if end > CLUB_CLOSE_TIME and end != time(0, 0):
            raise ClubClosedError(f"Club closes at {CLUB_CLOSE_TIME.strftime('%H:%M')}")

        if start_time.date() != end_time.date():
            raise ClubClosedError(detail="Overnight reservations not allowed")

    async def validate_group_availability(
        self,
        court_number: int,
        start_time: datetime,
        end_time: datetime,
        service_id: int | None,
        max_capacity: int,
        user_id: int,
    ) -> None:
        """Validate that group reservation does not exceed court capacity and user is not double-booked."""
        statement = select(Reservation).where(
            Reservation.court_number == court_number,
            Reservation.service_id == service_id,
            Reservation.start_time >= start_time,
            Reservation.end_time <= end_time,  # type: ignore
            Reservation.status != ReservationStatus.CANCELLED,
        )
        result = await self.session.execute(statement)
        overlapping_reservations = result.scalars().all()

        current_participants = 0
        for res in overlapping_reservations:
            if res.service_id != service_id:
                raise ForbiddenActionError(
                    detail="Court is booked for another activity."
                )

            if res.user_id == user_id:
                raise DoubleCourtBookingError(
                    detail="You already have a reservation for this time slot."
                )

            current_participants += 1

        if current_participants >= max_capacity:
            raise ForbiddenActionError(
                detail=f"Max group capacity reached: {max_capacity}"
            )
