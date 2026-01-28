"""Coach service management.
Handles coach service creation, reservations, and availability queries.
"""

from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col
from ..models.service import Service, ServiceCreate, ServiceCategory
from ..models.user import User, Role
from ..models.reservation import Reservation, ReservationStatus
from ..core.exceptions import (
    ReservationNotFoundError,
    ServiceNotChosenError,
    ForbiddenActionError,
    ServiceNotFoundError,
)


class CoachService:
    """Service for managing coaching services.
    Handles service creation, deletion, reservation management, and availability filtering.
    """

    def __init__(self, session: AsyncSession):
        """Initialize CoachService with database session.
        Args:
            session: Async SQLAlchemy database session.
        """
        self.session = session

    async def create_new_service(
        self, user: User, service_input: ServiceCreate
    ) -> Service:
        """Create a new coaching service.
        Admin can create services for any coach, coaches create for themselves.
        Args:
            user: The coach or admin creating the service.
            service_input: Service creation data.
        Returns:
            Service: The newly created service.
        """
        target_coach = None
        target_coach_id = None

        if user.role == Role.ADMIN:
            if not service_input.coach_id:
                raise ValueError(
                    "Coach ID must be provided by admin when creating a service."
                )

            found_coach = await self.session.get(User, service_input.coach_id)

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

        self.session.add(service)
        await self.session.commit()
        await self.session.refresh(service)

        return service

    @staticmethod
    def get_services_by_coach(user: User) -> list[Service]:
        """Get all services provided by a coach.
        Args:
            user: The coach user.
        Returns:
            list[Service]: All services for this coach.
        """
        return user.services

    async def get_reservations_for_coach(self, user: User) -> Sequence[Reservation]:
        """Get all reservations for a coach's services.
        Args:
            user: The coach user.
        Returns:
            Sequence[Reservation]: All reservations for coach's services.
        """
        coach_services_ids = [s.id for s in user.services if s.id is not None]

        if not coach_services_ids:
            return []

        statement = select(Reservation).where(
            col(Reservation.service_id).in_(coach_services_ids)
        )
        result = await self.session.execute(statement)
        reservations = result.scalars().all()

        return reservations

    async def process_reservation_confirmation(
        self, user: User, reservation_id: int
    ) -> Reservation:
        """Confirm a pending reservation (coach only).
        Args:
            user: The coach confirming the reservation.
            reservation_id: ID of the reservation to confirm.
        Returns:
            Reservation: The confirmed reservation.
        """
        reservation = await self.session.get(Reservation, reservation_id)
        if not reservation:
            raise ReservationNotFoundError()

        service = await self.session.get(Service, reservation.service_id)

        if not service:
            raise ServiceNotChosenError()

        if service.coach_id != user.id:
            raise ForbiddenActionError()

        reservation.status = ReservationStatus.CONFIRMED

        self.session.add(reservation)
        await self.session.commit()
        await self.session.refresh(reservation)

        return reservation

    async def select_available_services(
        self,
        name: str | None = None,
        category: ServiceCategory | None = None,
    ) -> Sequence[Service]:
        """Get available coaching services, optionally filtered.
        Args:
            name: Filter by service name (substring match).
            category: Filter by service category.
        Returns:
            Sequence[Service]: Available services matching filters.
        """
        statement = select(Service).where(Service.is_available is True)

        if name:
            statement = statement.where(col(Service.name).ilike(f"%{name}%"))

        if category:
            statement = statement.where(Service.category == category)

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def remove_service(self, service_id: int, current_user: User) -> dict:
        """Delete a coaching service.
        Args:
            service_id: ID of the service to delete.
            current_user: The user requesting deletion.
        Returns:
            dict: Success message.
        Raises:
            ServiceNotFoundError: If service doesn't exist.
        """
        service = await self.session.get(Service, service_id)
        if not service:
            raise ServiceNotFoundError()

        await self.session.delete(service)
        await self.session.commit()
        return {"msg": "Service deleted successfully"}
