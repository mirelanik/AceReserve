import pytest
from sqlalchemy import select
from ..conftest import get_auth_header
from src.models.user import User
from src.models.loyalty import LoyaltyAccount, LoyaltyLevel


@pytest.mark.asyncio
async def test_api_get_loyalty_info(client, session, sample_user):
    current_user = await session.get(User, sample_user.id)
    result = await session.execute(
        select(LoyaltyAccount).where(LoyaltyAccount.user_id == current_user.id)
    )
    current_account = result.scalars().first()

    headers = get_auth_header(current_user.id)
    response = await client.get("/loyalty/info", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == current_account.user_id
    assert data["points"] == current_account.points
    assert data["level"] == current_account.level


@pytest.mark.asyncio
async def test_api_adjust_loyalty_points(client, session, sample_user, sample_admin):
    current_user = await session.get(User, sample_user.id)
    current_admin = await session.get(User, sample_admin.id)
    result = await session.execute(
        select(LoyaltyAccount).where(LoyaltyAccount.user_id == current_user.id)
    )
    current_account = result.scalars().first()
    initial_points = current_account.points

    payload = {
        "user_id": current_user.id,
        "points_change": 100,
        "reason": "Test adjustment",
    }
    headers = get_auth_header(current_admin.id)
    response = await client.post("/loyalty/adjust", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == current_user.id
    assert data["points"] == initial_points + 100
    assert data["level"] == LoyaltyLevel.SILVER
