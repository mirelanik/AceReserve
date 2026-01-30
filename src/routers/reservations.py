"""Reservation management API endpoints.
Handles reservation creation, retrieval, modification, and cancellation.
"""

from fastapi import APIRouter, Depends
from ..models.reservation import ReservationRead, ReservationCreate, ReservationUpdate
from ..models.user import User
from ..auth.dependencies import require_user
from ..core.dependencies_services import get_reservation_service
from ..services.reservation_service import ReservationService

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.post("/", response_model=ReservationRead, status_code=201)
async def create_reservation(
    reservation_input: ReservationCreate,
    current_user: User = Depends(require_user),
    service: ReservationService = Depends(get_reservation_service),
):
    return await service.process_reservation_creation(current_user, reservation_input)


@router.get("/me", response_model=list[ReservationRead], status_code=200)
async def show_my_reservations(
    current_user: User = Depends(require_user),
    service: ReservationService = Depends(get_reservation_service),
):
    return await service.get_user_reservations(current_user)


@router.patch("/{reservation_id}", status_code=200)
async def cancel_reservation(
    reservation_id: int,
    current_user: User = Depends(require_user),
    service: ReservationService = Depends(get_reservation_service),
):
    return await service.delete_reservation(current_user, reservation_id)


@router.put("/{reservation_id}", response_model=ReservationRead, status_code=200)
async def edit_reservation(
    reservation_id: int,
    update_data: ReservationUpdate,
    current_user=Depends(require_user),
    service: ReservationService = Depends(get_reservation_service),
):
    return await service.modify_reservation(current_user, reservation_id, update_data)
