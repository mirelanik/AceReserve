"""Helper methods for validating reservations."""

from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from ..core.exceptions import (
    StartTimeError,
    DoubleCourtBookingError,
    DoubleCoachBookingError,
    ServiceNotFoundError,
    LightingAvailabilityError,
    LightingTimeError,
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
            Reservation.end_time > start_time,
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
