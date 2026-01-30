import pytest
from sqlalchemy import select
from src.services.loyalty_service import LoyaltyService
from src.models.loyalty import LoyaltyAccount, LoyaltyLevel
from src.models.user import User
from src.core.exceptions import LoyaltyAccountNotFoundError


@pytest.mark.parametrize(
    "initial_points, points_to_add, expected_level, expected_total",
    [
        (40, 10, LoyaltyLevel.SILVER, 50),
        (140, 10, LoyaltyLevel.GOLD, 150),
        (290, 10, LoyaltyLevel.PLATINUM, 300),
    ],
)
@pytest.mark.asyncio
async def test_loyalty_level_upgrades(
    initial_points, points_to_add, expected_level, expected_total
):
    account = LoyaltyAccount(
        user_id=1, points=initial_points, level=LoyaltyLevel.BEGINNER
    )
    LoyaltyService.update_loyalty_level(account, points_to_add)

    assert account.points == expected_total
    assert account.level == expected_level


@pytest.mark.asyncio
async def test_get_loyalty_info_existing_user(session, sample_user):
    service = LoyaltyService(session)

    user = await session.get(User, sample_user.id)
    info = await service.get_loyalty_info(user)

    assert info.points == 0
    assert info.level == LoyaltyLevel.BEGINNER


@pytest.mark.asyncio
async def test_change_loyalty_points(session, sample_user):
    service = LoyaltyService(session)
    user_id = sample_user.id

    updated_account = await service.change_loyalty_points(sample_user.id, 20)

    assert updated_account.points == 20

    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    loaded_user = result.scalars().first()
    await session.refresh(loaded_user, ["loyalty"])

    assert loaded_user.loyalty.points == 20


@pytest.mark.asyncio
async def test_change_loyalty_points_level_up(session, sample_user):
    service = LoyaltyService(session)
    user_id = sample_user.id

    updated_account = await service.change_loyalty_points(sample_user.id, 60)

    assert updated_account.points == 60
    assert updated_account.level == LoyaltyLevel.SILVER

    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)

    loaded_user = result.scalars().first()
    await session.refresh(loaded_user, ["loyalty"])

    assert loaded_user.loyalty.level == LoyaltyLevel.SILVER


@pytest.mark.asyncio
async def test_change_loyalty_account_not_found(session):
    service = LoyaltyService(session)

    user = User(
        email="noloyalty@test.com",
        full_name="No Loyalty User",
        hashed_password="pwd",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    with pytest.raises(LoyaltyAccountNotFoundError):
        await service.change_loyalty_points(user.id, 10)
