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
    return await service.create_new_service(current_coach, service_input)


@router.get("/reservations", response_model=list[ReservationRead], status_code=200)
async def get_coach_reservations(
    current_coach: User = Depends(require_coach),
    service: CoachService = Depends(get_coach_service),
):
    return await service.get_reservations_for_coach(current_coach)


@router.get("/services", response_model=list[ServiceRead], status_code=200)
async def get_coach_services(
    current_coach: User = Depends(require_coach),
):
    return CoachService.get_services_by_coach(current_coach)


@router.get("/services/available", response_model=list[ServiceRead], status_code=200)
async def get_available_services(
    name: str | None = Query(None, description="Search by service name"),
    category: ServiceCategory | None = Query(None, description="Search by category"),
    service: CoachService = Depends(get_coach_service),
):
    return await service.select_available_services(name, category)


@router.delete("/services/{service_id}", status_code=200)
async def delete_service(
    service_id: int,
    current_user: User = Depends(require_coach),
    service: CoachService = Depends(get_coach_service),
):
    return await service.remove_service(service_id, current_user)
