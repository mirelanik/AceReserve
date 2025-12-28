from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..database import get_session
from ..models.court import CourtCreate, CourtRead
from ..models.user import User, Role
from ..auth.security import get_current_user
from ..core.exceptions import ForbiddenActionError
from ..services.court_service import create_court, get_all_courts, get_court_by_number


router = APIRouter(prefix="/courts", tags=["Courts"])


@router.post("/", response_model=CourtRead)
def add_court(
    court_input: CourtCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != Role.ADMIN:
        raise ForbiddenActionError()
    return create_court(session, court_input)


@router.get("/", response_model=list[CourtRead])
def show_courts(session: Session = Depends(get_session)):
    return get_all_courts(session)


@router.get("/{court_number}", response_model=CourtRead)
def show_current_court(court_number: int, session: Session = Depends(get_session)):
    return get_court_by_number(session, court_number)