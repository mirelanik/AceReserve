from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..core.database import get_session
from ..auth.dependencies import require_user
from ..models.user import User
from ..models.review import ReviewCreate, ReviewRead
from ..services.review_service import (
    add_review,
    show_court_reviews,
    show_service_reviews,
    show_coach_reviews,
    calculate_average_rating,
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewRead)
def create_review(
    review_input: ReviewCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_user),
):
    review = add_review(session, current_user, review_input)
    review.user = current_user
    return review


@router.get("/court/{court_number}", response_model=list[ReviewRead])
def get_court_reviews(
    court_number: int,
    session: Session = Depends(get_session),
):
    reviews = show_court_reviews(session, court_number)
    return reviews


@router.get("/service/{service_id}", response_model=list[ReviewRead])
def get_service_reviews(
    service_id: int,
    session: Session = Depends(get_session),
):
    reviews = show_service_reviews(session, service_id)
    return reviews


@router.get("/coach/{coach_id}", response_model=list[ReviewRead])
def get_coach_reviews(
    coach_id: int,
    session: Session = Depends(get_session),
):
    reviews = show_coach_reviews(session, coach_id)
    return reviews


@router.get("/average-rating")
def get_average_rating(
    court_number: int | None = None,
    service_id: int | None = None,
    coach_id: int | None = None,
    session: Session = Depends(get_session),
):
    average = calculate_average_rating(
        court_number=court_number,
        service_id=service_id,
        coach_id=coach_id,
        session=session,
    )

    return {"average_rating": average}
