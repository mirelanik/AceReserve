import pytest
from decimal import Decimal
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.reservation import ReservationCreate
from src.models.user import User
from src.services.pricing_service import PricingService
from src.models.loyalty import LoyaltyLevel


@pytest.mark.asyncio
async def test_calculate_price_beginner_no_extras(session, sample_user, sample_court):
    service = PricingService(session)
    reservation_data = ReservationCreate(
        court_number=sample_court.number,
        start_time=datetime(2026, 1, 18, 10, 0, 0),
        duration_minutes=60,
        rent_racket=False,
        rent_balls=False,
        wants_lighting=False,
    )

    price = service.calculate_price(sample_court, reservation_data, sample_user)

    assert price == Decimal("25.00")


@pytest.mark.asyncio
async def test_calculate_price_gold_with_extras(session, sample_user, sample_court):
    service = PricingService(session)

    stmt = (
        select(User)
        .options(selectinload(User.loyalty)) # type: ignore
        .where(User.id == sample_user.id)
    )
    result = await session.execute(stmt)
    user = result.scalar_one()

    court = await session.merge(sample_court)

    user.loyalty.level = LoyaltyLevel.GOLD
    session.add(user)
    await session.commit()
    await session.refresh(user)

    reservation_data = ReservationCreate(
        court_number=court.number,
        start_time=datetime(2026, 1, 18, 20, 0, 0),
        duration_minutes=120,
        rent_racket=True,
        rent_balls=True,
        wants_lighting=True,
    )

    price = service.calculate_price(court, reservation_data, user)

    assert price == Decimal("61.20")
