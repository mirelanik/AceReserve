from decimal import Decimal
import pytest
from src.services.favorites_services import FavoritesService
from src.models.user import User, Role
from src.models.court import Court, Surface
from src.core.exceptions import (
    CourtNotFoundError,
    FavoriteAlreadyExistsError,
    CoachNotFoundError,
)


@pytest.mark.asyncio
async def test_add_court_to_favorites(session, sample_user, sample_court):
    service = FavoritesService(session)
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    result = await service.add_court_to_favorites(merged_user, merged_court.number)

    assert result["message"] == f"Court {merged_court.number} added to favorites."
    await session.refresh(merged_user)
    assert merged_court in merged_user.favorite_courts


@pytest.mark.asyncio
async def test_add_nonexistent_court_to_favorites(session, sample_user):
    service = FavoritesService(session)
    merged_user = await session.merge(sample_user)

    with pytest.raises(CourtNotFoundError):
        await service.add_court_to_favorites(merged_user, 999)


@pytest.mark.asyncio
async def test_add_duplicate_favorite_court(session, sample_user, sample_court):
    service = FavoritesService(session)
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    await service.add_court_to_favorites(merged_user, merged_court.number)

    with pytest.raises(FavoriteAlreadyExistsError):
        await service.add_court_to_favorites(merged_user, merged_court.number)


@pytest.mark.asyncio
async def test_remove_court_from_favorites(session, sample_user, sample_court):
    service = FavoritesService(session)
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    await service.add_court_to_favorites(merged_user, merged_court.number)
    result = await service.remove_court_from_favorites(merged_user, merged_court.number)

    assert result["message"] == f"Court {merged_court.number} removed from favorites."
    await session.refresh(merged_user)
    assert merged_court not in merged_user.favorite_courts


@pytest.mark.asyncio
async def test_list_favorite_courts_multiple(session, sample_user):
    merged_user = await session.merge(sample_user)

    court2 = Court(
        number=2,
        surface=Surface.CLAY,
        price_per_hour=Decimal("30.00"),
    )
    court3 = Court(
        number=3,
        surface=Surface.GRASS,
        price_per_hour=Decimal("35.00"),
    )

    session.add(court2)
    session.add(court3)
    await session.commit()

    service = FavoritesService(session)

    await service.add_court_to_favorites(merged_user, court2.number)
    await service.add_court_to_favorites(merged_user, court3.number)

    favorite_courts = FavoritesService.list_favorite_courts(merged_user)

    assert len(favorite_courts) == 2
    assert court2 in favorite_courts
    assert court3 in favorite_courts


@pytest.mark.asyncio
async def test_add_coach_to_favorites(session, sample_user, sample_coach):
    service = FavoritesService(session)
    merged_user = await session.merge(sample_user)
    merged_coach = await session.merge(sample_coach)

    result = await service.add_coach_to_favorites(merged_user, merged_coach.id)

    assert result["message"] == f"Coach {merged_coach.id} added to favorites."
    await session.refresh(merged_user)
    assert merged_coach in merged_user.favorite_coaches


@pytest.mark.asyncio
async def test_add_nonexistent_coach_to_favorites(session, sample_user):
    service = FavoritesService(session)
    merged_user = await session.merge(sample_user)

    with pytest.raises(CoachNotFoundError):
        await service.add_coach_to_favorites(merged_user, 999)


@pytest.mark.asyncio
async def test_add_duplicate_favorite_coach(session, sample_user, sample_coach):
    service = FavoritesService(session)
    merged_user = await session.merge(sample_user)
    merged_coach = await session.merge(sample_coach)

    await service.add_coach_to_favorites(merged_user, merged_coach.id)

    with pytest.raises(FavoriteAlreadyExistsError):
        await service.add_coach_to_favorites(merged_user, merged_coach.id)


@pytest.mark.asyncio
async def test_remove_coach_from_favorites(session, sample_user, sample_coach):
    service = FavoritesService(session)
    merged_user = await session.merge(sample_user)
    merged_coach = await session.merge(sample_coach)

    await service.add_coach_to_favorites(merged_user, merged_coach.id)
    result = await service.remove_coach_from_favorites(merged_user, merged_coach.id)

    assert result["message"] == f"Coach {merged_coach.id} removed from favorites."
    await session.refresh(merged_user)
    assert merged_coach not in merged_user.favorite_coaches


@pytest.mark.asyncio
async def test_list_favorite_coaches_multiple(session, sample_user):
    merged_user = await session.merge(sample_user)

    coach1 = User(
        email="coach1@test.com",
        full_name="Coach 1",
        hashed_password="pwd",
        role=Role.COACH,
    )
    coach2 = User(
        email="coach2@test.com",
        full_name="Coach 2",
        hashed_password="pwd",
        role=Role.COACH,
    )

    session.add(coach1)
    session.add(coach2)
    await session.commit()
    await session.refresh(coach1)
    await session.refresh(coach2)

    service = FavoritesService(session)

    await service.add_coach_to_favorites(merged_user, coach1.id)
    await service.add_coach_to_favorites(merged_user, coach2.id)

    favorite_coaches = FavoritesService.list_favorite_coaches(merged_user)

    assert len(favorite_coaches) == 2
    assert coach1 in favorite_coaches
    assert coach2 in favorite_coaches
