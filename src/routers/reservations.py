from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..models.reservation import ReservationRead, ReservationCreate
from ..models.user import User, Role
from ..auth.dependencies import require_user
from ..database import get_session
from ..core.exceptions import NotLoggedInError
from ..services.reservation_service import (
    process_reservation_creation,
    get_user_reservations,
    delete_reservation,
)

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.post("/", response_model=ReservationRead)
def create_reservation(
    reservation_input: ReservationCreate,
    current_user: User = Depends(require_user),
    session: Session = Depends(get_session),
):
    if current_user.role == Role.GUEST:
        raise NotLoggedInError()

    new_reservation = process_reservation_creation(
        session, current_user, reservation_input
    )

    return new_reservation


@router.get("/", response_model=list[ReservationRead])
def show_my_reservations(
    session: Session = Depends(get_session), current_user=Depends(require_user)
):
    return get_user_reservations(session, current_user)


@router.patch("/{reservation_id}/cancel")
def cancel_reservation(
    reservation_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_user),
):
    return delete_reservation(session, current_user, reservation_id)
