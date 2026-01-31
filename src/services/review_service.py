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
    ) -> dict:
        """Calculate average rating(s) for court, service, coach, or overall.
        Returns a dict with keys depending on parameters provided.
       """
        response: dict = {}

        if court_number is not None:
            court_query = select(func.avg(Review.rating)).where(
                Review.court_number == court_number
            )
            court_result = await self.session.execute(court_query)
            court_avg = court_result.scalar()
            response["court_average"] = round(court_avg, 1) if court_avg is not None else None

        if service_id is not None:
            service_query = select(func.avg(Review.rating)).where(Review.service_id == service_id)
            service_result = await self.session.execute(service_query)
            service_avg = service_result.scalar()
            response["service_average"] = round(service_avg, 1) if service_avg is not None else None

        if coach_id is not None:
            coach_query = select(func.avg(Review.rating)).where(Review.coach_id == coach_id)
            coach_result = await self.session.execute(coach_query)
            coach_avg = coach_result.scalar()
            response["coach_average"] = round(coach_avg, 1) if coach_avg is not None else None

        if not response:
            query = select(func.avg(Review.rating))
            result = await self.session.execute(query)
            avg_value = result.scalar()
            return {"average": round(avg_value, 1) if avg_value is not None else None}

        return response
