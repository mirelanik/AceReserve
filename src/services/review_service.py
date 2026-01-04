from sqlmodel import Session, func
from typing import Sequence
from sqlmodel import select
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


def add_review(session: Session, author: User, review_input: ReviewCreate) -> Review:
    if review_input.court_number and review_input.coach_id:
        raise MoreTargetTypesError()

    if not (
        review_input.court_number or review_input.coach_id or review_input.service_id
    ):
        raise NoTargetTypeError()

    if review_input.court_number:
        if not session.get(Court, review_input.court_number):
            raise CourtNotFoundError()

    if review_input.service_id:
        if not session.get(Service, review_input.service_id):
            raise ServiceNotFoundError()

    if review_input.coach_id:
        if not session.get(User, review_input.coach_id):
            raise CoachNotFoundError()

    review = Review(**review_input.model_dump(exclude_unset=True), author_id=author.id)

    review = Review(
        author_id=author.id,
        rating=review_input.rating,
        comment=review_input.comment,
        target_type=review_input.target_type,
        court_number=review_input.court_number,
        coach_id=review_input.coach_id,
        service_id=review_input.service_id,
    )

    session.add(review)
    session.commit()
    session.refresh(review)
    return review


def show_court_reviews(session: Session, court_number: int) -> Sequence[Review]:
    return session.exec(select(Review).where(Review.court_number == court_number)).all()


def show_service_reviews(session: Session, service_id: int) -> Sequence[Review]:
    return session.exec(select(Review).where(Review.service_id == service_id)).all()


def show_coach_reviews(session: Session, coach_id: int) -> Sequence[Review]:
    return session.exec(select(Review).where(Review.coach_id == coach_id)).all()


def calculate_average_rating(
    session: Session,
    court_number: int | None = None,
    service_id: int | None = None,
    coach_id: int | None = None,
) -> float:
    query = select(func.avg(Review.rating))

    if court_number:
        query = query.where(Review.court_number == court_number)
    elif service_id:
        query = query.where(Review.service_id == service_id)
    elif coach_id:
        query = query.where(Review.coach_id == coach_id)
    else:
        return 0.0

    result = session.exec(query).first()
    return round(result, 1) if result else 0.0
