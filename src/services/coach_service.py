"""Coach service management.
Handles coach service creation, reservations, and availability queries.
"""

from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col
from ..models.service import Service, ServiceCreate, ServiceCategory
from ..models.user import User, Role
from ..models.reservation import Reservation
from ..core.exceptions import CoachNotFoundError, ServiceNotFoundError


class CoachService:
    """Service for managing coaching services.
    Handles service creation, deletion, reservation management, and availability filtering.
    """

    def __init__(self, session: AsyncSession):
        """Initialize CoachService with database session."""
        self.session = session

    async def create_new_service(
        self, user: User, service_input: ServiceCreate
    ) -> Service:
        """Create a new coaching service.
        Admin can create services for any coach, coaches create for themselves."""
        target_coach = None
        target_coach_id = None

        if user.role == Role.ADMIN:
            if not service_input.coach_id:
                raise ValueError(
                    "Coach ID must be provided by admin when creating a service."
                )

            found_coach = await self.session.get(User, service_input.coach_id)

            if not found_coach or found_coach.role != Role.COACH:
                raise CoachNotFoundError()

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
        """Get all services offered by the coach."""
        return user.services

    async def get_reservations_for_coach(self, user: User) -> Sequence[Reservation]:
        """Get all reservations for services offered by the coach."""
        coach_services_ids = [s.id for s in user.services if s.id is not None]

        if not coach_services_ids:
            return []

        statement = select(Reservation).where(
            col(Reservation.service_id).in_(coach_services_ids)
        )
        result = await self.session.execute(statement)
        reservations = result.scalars().all()

        return reservations

    async def select_available_services(
        self,
        name: str | None = None,
        category: ServiceCategory | None = None,
    ) -> Sequence[Service]:
        """Select available services with optional filtering by name and category."""
        statement = select(Service).where(Service.is_available == True)

        if name:
            statement = statement.where(col(Service.name).ilike(f"%{name}%"))

        if category:
            statement = statement.where(Service.category == category)

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def remove_service(self, service_id: int, current_user: User) -> dict:
        """Remove a service by ID. Only the coach who offers the service or an admin can remove it."""
        service = await self.session.get(Service, service_id)
        if not service:
            raise ServiceNotFoundError()

        await self.session.delete(service)
        await self.session.commit()
        return {"msg": "Service deleted successfully"}
