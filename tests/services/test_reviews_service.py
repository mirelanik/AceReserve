import pytest
from src.services.review_service import ReviewService
from src.models.review import ReviewCreate, ReviewTargetType
from src.core.exceptions import (
    MoreTargetTypesError,
    NoTargetTypeError,
    CourtNotFoundError,
    ServiceNotFoundError,
    CoachNotFoundError,
)


@pytest.mark.asyncio
async def test_review_multiple_targets_error(session, sample_user):
    service = ReviewService(session)
    review_input = ReviewCreate(
        rating=5, target_type=ReviewTargetType.COURT, court_number=1, coach_id=2
    )

    with pytest.raises(MoreTargetTypesError):
        await service.add_review(sample_user, review_input)


@pytest.mark.asyncio
async def test_review_no_target_error(session, sample_user):
    service = ReviewService(session)
    review_input = ReviewCreate(
        rating=5,
        target_type=ReviewTargetType.COURT,
    )

    with pytest.raises(NoTargetTypeError):
        await service.add_review(sample_user, review_input)


@pytest.mark.asyncio
async def test_add_court_review(session, sample_user, sample_court):
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    service = ReviewService(session)
    review_input = ReviewCreate(
        rating=5,
        comment="Great court!",
        target_type=ReviewTargetType.COURT,
        court_number=merged_court.number,
    )

    review = await service.add_review(merged_user, review_input)

    assert review.author_id == merged_user.id
    assert review.rating == 5
    assert review.court_number == merged_court.number
    assert review.id is not None


@pytest.mark.asyncio
async def test_add_review_nonexistent_court(session, sample_user):
    merged_user = await session.merge(sample_user)
    service = ReviewService(session)

    review_input = ReviewCreate(
        rating=5, target_type=ReviewTargetType.COURT, court_number=999
    )

    with pytest.raises(CourtNotFoundError):
        await service.add_review(merged_user, review_input)


@pytest.mark.asyncio
async def test_add_service_review(session, sample_user, sample_service):
    merged_user = await session.merge(sample_user)
    merged_service = await session.merge(sample_service)

    service = ReviewService(session)
    review_input = ReviewCreate(
        rating=4,
        comment="Good service",
        target_type=ReviewTargetType.SERVICE,
        service_id=merged_service.id,
    )

    review = await service.add_review(merged_user, review_input)

    assert review.rating == 4
    assert review.service_id == merged_service.id


@pytest.mark.asyncio
async def test_add_review_nonexistent_service(session, sample_user):
    merged_user = await session.merge(sample_user)
    service = ReviewService(session)

    review_input = ReviewCreate(
        rating=5, target_type=ReviewTargetType.SERVICE, service_id=999
    )

    with pytest.raises(ServiceNotFoundError):
        await service.add_review(merged_user, review_input)


@pytest.mark.asyncio
async def test_add_coach_review(session, sample_user, sample_coach):
    merged_user = await session.merge(sample_user)
    merged_coach = await session.merge(sample_coach)

    service = ReviewService(session)
    review_input = ReviewCreate(
        rating=5,
        comment="Excellent coach!",
        target_type=ReviewTargetType.COACH,
        coach_id=merged_coach.id,
    )

    review = await service.add_review(merged_user, review_input)

    assert review.rating == 5
    assert review.coach_id == merged_coach.id


@pytest.mark.asyncio
async def test_add_review_nonexistent_coach(session, sample_user):
    merged_user = await session.merge(sample_user)
    service = ReviewService(session)

    review_input = ReviewCreate(
        rating=5, target_type=ReviewTargetType.COACH, coach_id=999
    )

    with pytest.raises(CoachNotFoundError):
        await service.add_review(merged_user, review_input)


@pytest.mark.asyncio
async def test_show_court_reviews(
    session, sample_user, sample_user_other, sample_court
):
    merged_user = await session.merge(sample_user)
    merged_other = await session.merge(sample_user_other)
    merged_court = await session.merge(sample_court)

    service = ReviewService(session)

    await service.add_review(
        merged_user,
        ReviewCreate(
            rating=5,
            comment="Great!",
            target_type=ReviewTargetType.COURT,
            court_number=merged_court.number,
        ),
    )

    await service.add_review(
        merged_other,
        ReviewCreate(
            rating=3,
            comment="Okay.",
            target_type=ReviewTargetType.COURT,
            court_number=merged_court.number,
        ),
    )

    reviews = await service.show_court_reviews(merged_court.number)

    assert len(reviews) == 2
    assert any(r.rating == 5 for r in reviews)
    assert any(r.rating == 3 for r in reviews)


@pytest.mark.asyncio
async def test_show_service_reviews(session, sample_user, sample_service):
    merged_user = await session.merge(sample_user)
    merged_service = await session.merge(sample_service)

    service = ReviewService(session)
    await service.add_review(
        merged_user,
        ReviewCreate(
            rating=5, target_type=ReviewTargetType.SERVICE, service_id=merged_service.id
        ),
    )

    reviews = await service.show_service_reviews(merged_service.id)
    assert len(reviews) == 1
    assert reviews[0].service_id == merged_service.id


@pytest.mark.asyncio
async def test_show_coach_reviews(session, sample_user, sample_coach):
    merged_user = await session.merge(sample_user)
    merged_coach = await session.merge(sample_coach)

    service = ReviewService(session)
    await service.add_review(
        merged_user,
        ReviewCreate(
            rating=5, target_type=ReviewTargetType.COACH, coach_id=merged_coach.id
        ),
    )

    reviews = await service.show_coach_reviews(merged_coach.id)
    assert len(reviews) == 1
    assert reviews[0].coach_id == merged_coach.id


@pytest.mark.asyncio
async def test_calculate_average_rating_court(
    session, sample_user, sample_user_other, sample_court
):
    merged_user = await session.merge(sample_user)
    merged_other = await session.merge(sample_user_other)
    merged_court = await session.merge(sample_court)

    service = ReviewService(session)

    await service.add_review(
        merged_user,
        ReviewCreate(
            rating=5,
            target_type=ReviewTargetType.COURT,
            court_number=merged_court.number,
        ),
    )
    await service.add_review(
        merged_other,
        ReviewCreate(
            rating=4,
            target_type=ReviewTargetType.COURT,
            court_number=merged_court.number,
        ),
    )

    avg_rating = await service.calculate_average_rating(
        court_number=merged_court.number
    )
    assert avg_rating == 4.5
