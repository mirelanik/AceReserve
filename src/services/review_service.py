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
        self.session = session

    async def add_review(self, author: User, review_input: ReviewCreate) -> Review:
        """Create a new review for a court, service, or coach."""

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
        result = await self.session.execute(
            select(Review).where(Review.court_number == court_number)
        )
        return result.scalars().all()

    async def show_service_reviews(self, service_id: int) -> Sequence[Review]:
        result = await self.session.execute(
            select(Review).where(Review.service_id == service_id)
        )
        return result.scalars().all()

    async def show_coach_reviews(self, coach_id: int) -> Sequence[Review]:
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
        """Calculate average rating for a court, service, or coach."""
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
