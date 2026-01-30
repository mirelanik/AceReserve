"""Court management service.
Handles court creation, deletion, and availability queries.
"""

from typing import Sequence
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col
from ..models.court import CourtCreate, Court, Surface
from ..core.exceptions import ExistingCourtError, CourtNotFoundError
from ..models.reservation import Reservation, ReservationStatus
from ..models.user import User


class CourtService:
    """Service for managing tennis courts.
    Handles court creation, deletion, availability checking, and filtering.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_court(self, court_input: CourtCreate, current_user: User) -> Court:
        """Create a new court (admin only)."""
        result = await self.session.execute(
            select(Court).where(Court.number == court_input.number)
        )
        existing_court = result.scalars().first()

        if existing_court:
            raise ExistingCourtError()

        new_court = Court.model_validate(court_input)

        self.session.add(new_court)
        await self.session.commit()
        await self.session.refresh(new_court)

        return new_court

    async def remove_court(self, court_number: int, current_user: User) -> dict:
        """Delete a court (admin only)."""
        court = await self.session.get(Court, court_number)
        if not court:
            raise CourtNotFoundError()

        await self.session.delete(court)
        await self.session.commit()
        return {"msg": f"Court number {court_number} deleted successfully"}

    async def show_all_courts(self) -> Sequence[Court]:
        """Get all courts in the system."""
        result = await self.session.execute(select(Court))
        return result.scalars().all()

    async def show_court_by_number(self, court_number: int) -> Court:
        """Get a court by its number."""
        result = await self.session.execute(
            select(Court).where(Court.number == court_number)
        )
        court = result.scalars().first()
        if not court:
            raise CourtNotFoundError()

        return court

    async def select_courts_by_category(
        self,
        surface: str | None = None,
        lighting: bool | None = None,
        start_datetime: datetime | None = None,
        duration: int = 60,
    ) -> Sequence[Court]:
        """Get courts filtered by surface, lighting, and availability."""

        statement = select(Court).where(Court.available == True)

        if surface:
            try:
                surface_enum = Surface(surface.lower())
                statement = statement.where(Court.surface == surface_enum)
            except ValueError:
                pass

        if lighting is not None:
            statement = statement.where(Court.has_lighting == lighting)

        if start_datetime:
            end_datetime = start_datetime + timedelta(minutes=duration)
            busy_courts_statement = select(Reservation.court_number).where(
                Reservation.status != ReservationStatus.CANCELLED,
                Reservation.start_time < end_datetime,
                Reservation.end_time > start_datetime,
            )
            busy_result = await self.session.execute(busy_courts_statement)
            busy_court_ids = busy_result.scalars().all()

            if busy_court_ids:
                statement = statement.where(col(Court.number).not_in(busy_court_ids))

        courts_result = await self.session.execute(statement)
        return courts_result.scalars().all()
