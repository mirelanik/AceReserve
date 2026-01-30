import pytest
from ..conftest import get_auth_header
from src.services.favorites_services import FavoritesService
from src.models.user import Role, User


@pytest.mark.asyncio
async def test_api_add_court_to_favorites(client, session, sample_user, sample_court):
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    headers = get_auth_header(merged_user.id)

    response = await client.post(
        f"/favorites/courts/{merged_court.number}", headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "added to favorites" in data["message"]

    await session.refresh(merged_user)
    assert merged_court in merged_user.favorite_courts


@pytest.mark.asyncio
async def test_api_remove_favorite_court(client, session, sample_user, sample_court):
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    service = FavoritesService(session)
    await service.add_court_to_favorites(merged_user, merged_court.number)

    headers = get_auth_header(merged_user.id)
    response = await client.delete(
        f"/favorites/courts/{merged_court.number}", headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "removed from favorites" in data["message"]

    await session.refresh(merged_user)
    assert merged_court not in merged_user.favorite_courts


@pytest.mark.asyncio
async def test_api_list_favorite_courts(client, session, sample_user, sample_court):
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    service = FavoritesService(session)
    await service.add_court_to_favorites(merged_user, merged_court.number)

    headers = get_auth_header(merged_user.id)
    response = await client.get("/favorites/courts", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["number"] == merged_court.number


@pytest.mark.asyncio
async def test_api_add_nonexistent_court(client, session, sample_user):
    merged_user = await session.merge(sample_user)
    headers = get_auth_header(merged_user.id)

    response = await client.post("/favorites/courts/999", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_api_add_favorite_coach(client, session, sample_user, sample_coach):
    merged_user = await session.merge(sample_user)
    merged_coach = await session.merge(sample_coach)

    headers = get_auth_header(merged_user.id)

    response = await client.post(
        f"/favorites/coaches/{merged_coach.id}", headers=headers
    )

    assert response.status_code == 200

    data = response.json()
    assert "added to favorites" in data["message"]

    await session.refresh(merged_user)
    assert merged_coach in merged_user.favorite_coaches


@pytest.mark.asyncio
async def test_api_remove_favorite_coach(client, session, sample_user, sample_coach):
    merged_user = await session.merge(sample_user)
    merged_coach = await session.merge(sample_coach)

    service = FavoritesService(session)
    await service.add_coach_to_favorites(merged_user, merged_coach.id)

    headers = get_auth_header(merged_user.id)
    response = await client.delete(
        f"/favorites/coaches/{merged_coach.id}", headers=headers
    )

    assert response.status_code == 200

    await session.refresh(merged_user)
    assert merged_coach not in merged_user.favorite_coaches


@pytest.mark.asyncio
async def test_api_add_coach_invalid_role(client, session, sample_user):
    merged_user = await session.merge(sample_user)

    regular_user = User(
        email="regular@test.com",
        full_name="User",
        hashed_password="user123",
        role=Role.USER,
    )
    session.add(regular_user)
    await session.commit()
    await session.refresh(regular_user)

    headers = get_auth_header(merged_user.id)

    response = await client.post(
        f"/favorites/coaches/{regular_user.id}", headers=headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_api_list_favorite_coaches(client, session, sample_user, sample_coach):
    user_id = sample_user.id
    coach_id = sample_coach.id

    headers = get_auth_header(user_id)

    await client.post(f"/favorites/coaches/{coach_id}", headers=headers)

    response = await client.get("/favorites/coaches", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == coach_id
