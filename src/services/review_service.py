"""Review management service.
Handles review creation and retrieval for courts, services, and coaches.
"""

from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select
from ..models.review import Review, ReviewCreate
from ..models.user import User
from ..models.court import Court
from ..models.service import Service
from ..core.exceptions import (
    MoreTargetTypesError,
    NoTargetTypeError,
    CourtNotFoundError,
    ServiceNotFoundError,
    CoachNotFoundError,
)


class ReviewService:
    """Service for managing reviews.
    Handles review creation, retrieval, and rating calculations for courts, services, and coaches.
    """

    def __init__(self, session: AsyncSession):
        """Initialize ReviewService with database session.
        Args:
            session: Async SQLAlchemy database session.
        """
        self.session = session

    async def add_review(self, author: User, review_input: ReviewCreate) -> Review:
        """Create a new review for a court, service, or coach.
        Args:
            author: The user writing the review.
            review_input: Review creation data.
        Returns:
            Review: The newly created review.
        """
        if review_input.court_number and review_input.coach_id:
            raise MoreTargetTypesError()

        if not (
            review_input.court_number
            or review_input.coach_id
            or review_input.service_id
        ):
            raise NoTargetTypeError()

        if review_input.court_number:
            result = await self.session.execute(
                select(Court).where(Court.number == review_input.court_number)
            )
            court = result.scalars().first()
            if not court:
                raise CourtNotFoundError()

        if review_input.service_id:
            if not await self.session.get(Service, review_input.service_id):
                raise ServiceNotFoundError()

        if review_input.coach_id:
            if not await self.session.get(User, review_input.coach_id):
                raise CoachNotFoundError()

        review = Review(
            author_id=author.id,
            rating=review_input.rating,
            comment=review_input.comment,
            target_type=review_input.target_type,
            court_number=review_input.court_number,
            coach_id=review_input.coach_id,
            service_id=review_input.service_id,
        )

        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)
        return review

    async def show_court_reviews(self, court_number: int) -> Sequence[Review]:
        """Get all reviews for a specific court.
        Args:
            court_number: The court number.
        Returns:
            Sequence[Review]: All reviews for the court.
        """
        result = await self.session.execute(
            select(Review).where(Review.court_number == court_number)
        )
        return result.scalars().all()

    async def show_service_reviews(self, service_id: int) -> Sequence[Review]:
        """Get all reviews for a specific service.
        Args:
            service_id: The service ID.
        Returns:
            Sequence[Review]: All reviews for the service.
        """
        result = await self.session.execute(
            select(Review).where(Review.service_id == service_id)
        )
        return result.scalars().all()

    async def show_coach_reviews(self, coach_id: int) -> Sequence[Review]:
        """Get all reviews for a specific coach.
        Args:
            coach_id: The coach user ID.
        Returns:
            Sequence[Review]: All reviews for the coach.
        """
        result = await self.session.execute(
            select(Review).where(Review.coach_id == coach_id)
        )
        return result.scalars().all()

    async def calculate_average_rating(
        self,
        court_number: int | None = None,
        service_id: int | None = None,
        coach_id: int | None = None,
    ) -> float:
        """Calculate average rating for a court, service, or coach.
        Args:
            court_number: Court to get average for (optional).
            service_id: Service to get average for (optional).
            coach_id: Coach to get average for (optional).
        Returns:
            float: Average rating rounded to 1 decimal place, or 0.0 if no reviews.
        """
        query = select(func.avg(Review.rating))

        if court_number:
            query = query.where(Review.court_number == court_number)
        elif service_id:
            query = query.where(Review.service_id == service_id)
        elif coach_id:
            query = query.where(Review.coach_id == coach_id)
        else:
            return 0.0

        result = await self.session.execute(query)
        value = result.scalar_one_or_none()
        return round(value, 1) if value else 0.0
