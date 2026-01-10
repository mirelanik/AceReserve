from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..core.database import get_session
from ..auth.dependencies import require_coach, require_admin
from ..models.user import User
from ..models.service import ServiceRead, ServiceCreate, ServiceCategory
from ..models.reservation import ReservationRead
from ..services.coach_service import (
    create_new_service,
    get_reservations_for_coach,
    process_reservation_confirmation,
    remove_service,
    select_available_services,
)

router = APIRouter(prefix="/coach", tags=["Coaches"])


@router.post("/services", response_model=ServiceRead)
def create_service(
    service_input: ServiceCreate,
    session: Session = Depends(get_session),
    current_coach: User = Depends(require_coach),
):
    return create_new_service(session, current_coach, service_input)


@router.get("/reservations", response_model=list[ReservationRead])
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
def get_available_services(
    name: str | None = Query(None, description="Search by coach name"),
    category: ServiceCategory | None = Query(None, description="Search by category"),
    session: Session = Depends(get_session),
):
    return select_available_services(session, name, category)


@router.delete("/services/{service_id}")
def delete_service(
    service_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_coach or require_admin),
):
    return remove_service(service_id, current_user, session)
