from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..database import get_session
from ..auth.dependancies import get_current_coach
from ..models.user import User
from ..models.service import ServiceRead, ServiceCreate
from ..models.reservation import ReservationRead
from ..services.coach_service import (
    create_new_service,
    get_services_by_coach,
    get_reservations_for_coach,
    process_reservation_confirmation,
)

router = APIRouter(prefix="/coach", tags=["Coach"])


@router.post("/services", response_model=ServiceRead)
def create_service(
    service_input: ServiceCreate,
    current_coach: User = Depends(get_current_coach),
    session: Session = Depends(get_session),
):
    return create_new_service(session, current_coach, service_input)


@router.get("/services", response_model=list[ServiceRead])
def get_services(
    session: Session = Depends(get_session),
    current_coach: User = Depends(get_current_coach),
):
    return get_services_by_coach(session, current_coach)


@router.get("/coach_reservations", response_model=list[ReservationRead])
def get_coach_reservations(
    session: Session = Depends(get_session),
    current_coach: User = Depends(get_current_coach),
):
    return get_reservations_for_coach(session, current_coach)


@router.post("/reservations/{reservation_id}/confirm", response_model=ReservationRead)
def confirm_reservation(
    reservation_id: int,
    session: Session = Depends(get_session),
    current_coach: User = Depends(get_current_coach),
):
    return process_reservation_confirmation(session, current_coach, reservation_id)
