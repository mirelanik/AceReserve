import pytest
from decimal import Decimal
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.reservation import ReservationCreate
from src.models.user import User
from src.services.pricing_service import PricingService
from src.models.loyalty import LoyaltyLevel, LoyaltyAccount


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
    user = await session.get(User, sample_user.id)
    court = await session.merge(sample_court)
    
    statement = select(LoyaltyAccount).where(LoyaltyAccount.user_id == user.id)
    result = await session.execute(statement)
    loyalty_account= result.scalars().first()
    
    if loyalty_account:
        loyalty_account.level = LoyaltyLevel.GOLD
        session.add(loyalty_account)
    else:
        loyalty_account = LoyaltyAccount(
            user_id=user.id, 
            points=150, 
            level=LoyaltyLevel.GOLD
        )
        session.add(loyalty_account)

    await session.commit()
    await session.refresh(user, ["loyalty"])

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
