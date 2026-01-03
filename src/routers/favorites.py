from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..database import get_session
from ..models.user import User
from ..services.favorites_services import (
    add_court_to_favorites,
    remove_court_from_favorites,
    list_favorite_courts,
    add_coach_to_favorites,
    remove_coach_from_favorites,
    list_favorite_coaches,
)
from ..auth.dependencies import require_user

router = APIRouter(prefix="/favorites", tags=["Favorites"])

@router.post("/courts/{court_number}")
def add_court_favorite(
    court_number: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_user),
):
    return add_court_to_favorites(session, current_user, court_number)

@router.delete("/courts/{court_number}")
def remove_court_favorite(
    court_number: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_user),
):
    return remove_court_from_favorites(session, current_user, court_number)

@router.get("/courts")
def get_favorite_courts(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_user),
):
    return list_favorite_courts(session, current_user)

@router.post("/coaches/{coach_id}")
def add_coach_favorite(
    coach_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_user),
):
    return add_coach_to_favorites(session, current_user, coach_id)

@router.delete("/coaches/{coach_id}")
def remove_coach_favorite(
    coach_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_user),
):
    return remove_coach_from_favorites(session, current_user, coach_id)

@router.get("/coaches")
def get_favorite_coaches(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_user),
):
    return list_favorite_coaches(session, current_user)