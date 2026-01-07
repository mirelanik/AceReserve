from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from ..core.database import get_session
from ..models.court import CourtCreate, CourtRead
from ..models.user import User, Role
from ..auth.dependencies import require_user
from ..core.exceptions import ForbiddenActionError
from ..services.court_service import (
    create_court,
    show_all_courts,
    show_court_by_number,
    select_courts_by_category,
)


router = APIRouter(prefix="/courts", tags=["Courts"])


@router.post("/", response_model=CourtRead)
def add_court(
    court_input: CourtCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_user),
):
    if current_user.role != Role.ADMIN:
        raise ForbiddenActionError()
    return create_court(session, court_input)


@router.get("/all", response_model=list[CourtRead])
def get_all_courts(session: Session = Depends(get_session)):
    return show_all_courts(session)


@router.get("/{court_number}", response_model=CourtRead)
def get_current_court(court_number: int, session: Session = Depends(get_session)):
    return show_court_by_number(session, court_number)


@router.get("/", response_model=list[CourtRead])
def get_courts_by_category(
    surface: str | None = Query(None, description="Search by surface"),
    lighting: bool | None = Query(None, description="Search by lighting"),
    session: Session = Depends(get_session),
):
    return select_courts_by_category(session, surface, lighting)
