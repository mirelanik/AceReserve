from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..database import get_session
from ..auth.dependencies import require_coach
from ..models.user import User
from ..models.service import ServiceRead, ServiceCreate
from ..models.reservation import ReservationRead
from ..services.coach_service import (
    create_new_service,
    get_services_by_coach,
    get_reservations_for_coach,
    process_reservation_confirmation,
    get_all_available_services
)

router = APIRouter(prefix="/coach", tags=["Coaches"])


@router.post("/services", response_model=ServiceRead)
def create_service(
    service_input: ServiceCreate,
    current_coach: User = Depends(require_coach),
    session: Session = Depends(get_session),
):
    return create_new_service(session, current_coach, service_input)


@router.get("/coach_reservations", response_model=list[ReservationRead])
def get_coach_reservations(
    session: Session = Depends(get_session),
    current_coach: User = Depends(require_coach),
):
    return get_reservations_for_coach(session, current_coach)


@router.post("/reservations/{reservation_id}/confirm", response_model=ReservationRead)
def confirm_reservation(
    reservation_id: int,
    session: Session = Depends(get_session),
    current_coach: User = Depends(require_coach),
):
    return process_reservation_confirmation(session, current_coach, reservation_id)


@router.get("/services", response_model=list[ServiceRead])
def get_available_services(session: Session = Depends(get_session)):
    return get_all_available_services(session)
