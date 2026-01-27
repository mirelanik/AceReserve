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
    """Create a new court reservation.
    Validates court/coach availability, calculates price with discounts,
    and awards loyalty points.

    Args:
        reservation_input: Reservation creation data.
        current_user: The authenticated user making the reservation.
        service: ReservationService instance.
    Returns:
        ReservationRead: The created reservation.
    """
    return await service.process_reservation_creation(current_user, reservation_input)


@router.get("/me", response_model=list[ReservationRead], status_code=200)
async def show_my_reservations(
    current_user: User = Depends(require_user),
    service: ReservationService = Depends(get_reservation_service),
):
    """Get all reservations for the current user.
    Args:
        current_user: The authenticated user.
        service: ReservationService instance.
    Returns:
        list[ReservationRead]: All user's reservations.
    """
    return await service.get_user_reservations(current_user)


@router.patch("/{reservation_id}", status_code=200)
async def cancel_reservation(
    reservation_id: int,
    current_user: User = Depends(require_user),
    service: ReservationService = Depends(get_reservation_service),
):
    """Cancel a reservation.
    Args:
        reservation_id: ID of the reservation to cancel.
        current_user: The authenticated user (must own the reservation or be admin).
        service: ReservationService instance.
    Returns:
        dict: Success message.
    """
    return await service.delete_reservation(current_user, reservation_id)


@router.post("/{reservation_id}", response_model=ReservationRead, status_code=200)
async def edit_reservation(
    reservation_id: int,
    update_data: ReservationUpdate,
    current_user=Depends(require_user),
    service: ReservationService = Depends(get_reservation_service),
):
    """Update a reservation's details.
    Can modify court, date/time, duration, and extras. Revalidates availability
    and recalculates price if needed.

    Args:
        reservation_id: ID of the reservation to update.
        update_data: Updated reservation fields.
        current_user: The authenticated user (must own the reservation or be admin).
        service: ReservationService instance.
    Returns:
        ReservationRead: The updated reservation.
    """
    return await service.modify_reservation(current_user, reservation_id, update_data)
