"""Coach service management API endpoints.
Handles coach service creation, reservation management, and service queries.
"""

from fastapi import APIRouter, Depends, Query
from ..auth.dependencies import require_coach
from ..models.user import User
from ..models.service import ServiceRead, ServiceCreate, ServiceCategory
from ..models.reservation import ReservationRead
from ..core.dependencies_services import get_coach_service
from ..services.coach_service import CoachService

router = APIRouter(prefix="/coach", tags=["Coaches"])


@router.post("/services", response_model=ServiceRead, status_code=201)
async def create_service(
    service_input: ServiceCreate,
    current_coach: User = Depends(require_coach),
    service: CoachService = Depends(get_coach_service),
):
    """Create a new coaching service.
    Args:
        service_input: Service creation data.
        current_coach: The authenticated coach user.
        service: CoachService instance.
    Returns:
        ServiceRead: The newly created service.
    """
    return await service.create_new_service(current_coach, service_input)


@router.get("/reservations", response_model=list[ReservationRead], status_code=200)
async def get_coach_reservations(
    current_coach: User = Depends(require_coach),
    service: CoachService = Depends(get_coach_service),
):
    """Get all reservations for the coach's services.
    Args:
        current_coach: The authenticated coach user.
        service: CoachService instance.
    Returns:
        list[ReservationRead]: All reservations for coach's services.
    """
    return await service.get_reservations_for_coach(current_coach)


@router.get("/services", response_model=list[ServiceRead], status_code=200)
async def get_coach_services(
    current_coach: User = Depends(require_coach),
):
    """Get all services provided by the coach.
    Args:
        current_coach: The authenticated coach user.
    Returns:
        list[ServiceRead]: All services for this coach.
    """
    return CoachService.get_services_by_coach(current_coach)


@router.post("/reservations/{reservation_id}/confirm", response_model=ReservationRead, status_code=200)
async def confirm_reservation(
    reservation_id: int,
    current_coach: User = Depends(require_coach),
    service: CoachService = Depends(get_coach_service),
):
    """Confirm a pending reservation for coach's service.
    Args:
        reservation_id: ID of the reservation to confirm.
        current_coach: The authenticated coach user.
        service: CoachService instance.
    Returns:
        ReservationRead: The confirmed reservation.
    """
    return await service.process_reservation_confirmation(current_coach, reservation_id)


@router.get("/services/available", response_model=list[ServiceRead], status_code=200)
async def get_available_services(
    name: str | None = Query(None, description="Search by service name"),
    category: ServiceCategory | None = Query(None, description="Search by category"),
    service: CoachService = Depends(get_coach_service),
):
    """Search available coaching services.
    Args:
        name: Filter by service name (substring match).
        category: Filter by service category.
        service: CoachService instance.
    Returns:
        list[ServiceRead]: Available services matching filters.
    """
    return await service.select_available_services(name, category)


@router.delete("/services/{service_id}", status_code=200)
async def delete_service(
    service_id: int,
    current_user: User = Depends(require_coach),
    service: CoachService = Depends(get_coach_service),
):
    """Delete a coaching service.
    Args:
        service_id: ID of the service to delete.
        current_user: The authenticated coach user.
        service: CoachService instance.
    Returns:
        dict: Success message.
    """
    return await service.remove_service(service_id, current_user)
