from decimal import Decimal
import pytest
from src.services.court_service import CourtService
from src.models.court import CourtCreate, Court, Surface
from src.core.exceptions import ExistingCourtError, CourtNotFoundError


@pytest.fixture
def court_input():
    return CourtCreate(
        number=10,
        surface=Surface.CLAY,
        price_per_hour=Decimal("30.00"),
        has_lighting=True,
        available=True,
    )


@pytest.mark.asyncio
async def test_create_court(session, sample_admin, court_input):
    """Test creating a new court successfully."""
    service = CourtService(session)
    merged_admin = await session.merge(sample_admin)

    new_court = await service.create_court(court_input, merged_admin)

    assert new_court.id is not None
    assert new_court.number == 10
    assert new_court.surface == Surface.CLAY


@pytest.mark.asyncio
async def test_create_existing_court_error(session, sample_admin, sample_court):
    """Test creating a court with a number that already exists."""
    service = CourtService(session)
    merged_admin = await session.merge(sample_admin)
    merged_court = await session.merge(sample_court)

    duplicate_input = CourtCreate(
        number=merged_court.number,
        surface=Surface.HARD,
        price_per_hour=Decimal("20.00"),
    )

    with pytest.raises(ExistingCourtError):
        await service.create_court(duplicate_input, merged_admin)


@pytest.mark.asyncio
async def test_remove_court(session, sample_admin, sample_court):
    """Test deleting an existing court."""
    service = CourtService(session)
    merged_admin = await session.merge(sample_admin)
    merged_court = await session.merge(sample_court)

    response = await service.remove_court(merged_court.number, merged_admin)

    assert response["msg"] == f"Court number {merged_court.number} deleted successfully"

    deleted_court = await session.get(Court, merged_court.number)
    assert deleted_court is None


@pytest.mark.asyncio
async def test_remove_nonexistent_court(session, sample_admin):
    """Test deleting a court that does not exist."""
    service = CourtService(session)
    merged_admin = await session.merge(sample_admin)

    with pytest.raises(CourtNotFoundError):
        await service.remove_court(999, merged_admin)


@pytest.mark.asyncio
async def test_show_all_courts(session, sample_court):
    """Test retrieving all courts."""
    service = CourtService(session)

    court2 = Court(number=2, surface=Surface.GRASS, price_per_hour=Decimal("40"))
    session.add(court2)
    await session.commit()

    courts = await service.show_all_courts()

    assert len(courts) >= 2
    numbers = [c.number for c in courts]
    assert 1 in numbers
    assert 2 in numbers


@pytest.mark.asyncio
async def test_show_court_by_number(session, sample_court):
    """Test retrieving a specific court."""
    service = CourtService(session)
    merged_court = await session.merge(sample_court)
    court = await service.show_court_by_number(merged_court.number)

    assert court.id == merged_court.id


@pytest.mark.asyncio
async def test_show_court_by_number_not_found(session):
    service = CourtService(session)
    with pytest.raises(CourtNotFoundError):
        await service.show_court_by_number(999)


@pytest.mark.asyncio
async def test_filter_courts_by_attributes(session):
    """Test filtering by surface and lighting."""
    service = CourtService(session)

    c1 = Court(
        number=101,
        surface=Surface.HARD,
        has_lighting=True,
        available=True,
        price_per_hour=Decimal("10.00"),
    )
    c2 = Court(
        number=102,
        surface=Surface.CLAY,
        has_lighting=False,
        available=True,
        price_per_hour=Decimal("10.00"),
    )

    session.add_all([c1, c2])
    await session.commit()

    res_hard = await service.select_courts_by_category(surface="hard")
    assert len(res_hard) == 1
    assert res_hard[0].number == 101

    res_light = await service.select_courts_by_category(lighting=True)

    assert any(c.number == 101 for c in res_light)
    assert not any(c.number == 102 for c in res_light)
