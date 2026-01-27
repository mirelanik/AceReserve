"""Review management API endpoints.
Handles review creation and retrieval for courts, services, and coaches.
"""

from fastapi import APIRouter, Depends
from ..auth.dependencies import require_user
from ..models.user import User
from ..models.review import ReviewCreate, ReviewRead
from ..core.dependencies_services import get_review_service
from ..services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewRead, status_code=201)
async def create_review(
    review_input: ReviewCreate,
    current_user: User = Depends(require_user),
    service: ReviewService = Depends(get_review_service),
):
    """Create a new review for a court, service, or coach.
    Args:
        review_input: Review creation data.
        current_user: The authenticated user writing the review.
        service: ReviewService instance.
    Returns:
        ReviewRead: The created review.
    """
    review = await service.add_review(current_user, review_input)
    review.user = current_user
    return review


@router.get("/court/{court_number}", response_model=list[ReviewRead], status_code=200)
async def get_court_reviews(
    court_number: int,
    service: ReviewService = Depends(get_review_service),
):
    """Get all reviews for a specific court.
    Args:
        court_number: The court number.
        service: ReviewService instance.
    Returns:
        list[ReviewRead]: All reviews for the court.
    """
    return await service.show_court_reviews(court_number)


@router.get("/service/{service_id}", response_model=list[ReviewRead], status_code=200)
async def get_service_reviews(
    service_id: int,
    service: ReviewService = Depends(get_review_service),
):
    """Get all reviews for a specific service.
    Args:
        service_id: The service ID.
        service: ReviewService instance.
    Returns:
        list[ReviewRead]: All reviews for the service.
    """
    return await service.show_service_reviews(service_id)


@router.get("/coach/{coach_id}", response_model=list[ReviewRead], status_code=200)
async def get_coach_reviews(
    coach_id: int,
    service: ReviewService = Depends(get_review_service),
):
    """Get all reviews for a specific coach.
    Args:
        coach_id: The coach user ID.
        service: ReviewService instance.
    Returns:
        list[ReviewRead]: All reviews for the coach.
    """
    return await service.show_coach_reviews(coach_id)


@router.get("/average-rating", status_code=200)
async def get_average_rating(
    court_number: int | None = None,
    service_id: int | None = None,
    coach_id: int | None = None,
    service: ReviewService = Depends(get_review_service),
):
    """Calculate average rating for a court, service, or coach.
    Args:
        court_number: Court to get average for (optional).
        service_id: Service to get average for (optional).
        coach_id: Coach to get average for (optional).
        service: ReviewService instance.
    Returns:
        dict: Contains 'average_rating' key with float value.
    """
    average = await service.calculate_average_rating(
        court_number=court_number,
        service_id=service_id,
        coach_id=coach_id,
    )

    return {"average_rating": average}
