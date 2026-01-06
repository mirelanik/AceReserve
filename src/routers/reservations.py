from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..models.reservation import ReservationRead, ReservationCreate, ReservationUpdate
from ..models.user import User
from ..auth.dependencies import require_user, get_current_user
from ..core.database import get_session
from ..services.reservation_service import (
    process_reservation_creation,
    get_user_reservations,
    delete_reservation,
    modify_reservation,
)

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.post("/", response_model=ReservationRead)
def create_reservation(
    reservation_input: ReservationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_user),
):
    new_reservation = process_reservation_creation(
        session, current_user, reservation_input
    )

    return new_reservation


@router.get("/me", response_model=list[ReservationRead])
def show_my_reservations(
    session: Session = Depends(get_session), current_user: User = Depends(require_user)
):
    return get_user_reservations(session, current_user)


@router.patch("/{reservation_id}")
def cancel_reservation(
    reservation_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_user),
):
    return delete_reservation(session, current_user, reservation_id)


@router.post("/{reservation_id}", response_model=ReservationRead)
def edit_reservation(
    reservation_id: int,
    update_data: ReservationUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return modify_reservation(session, current_user, reservation_id, update_data)
