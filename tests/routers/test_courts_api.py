import pytest
from src.models.court import Surface, Court
from ..conftest import get_auth_header


@pytest.mark.asyncio
async def test_api_create_court_admin(client, sample_admin):
    headers = get_auth_header(sample_admin.id)
    payload = {
        "number": 5,
        "surface": "clay",
        "price_per_hour": 30.00,
        "has_lighting": True,
        "available": True,
    }
    response = await client.post("/courts/", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["number"] == 5


@pytest.mark.asyncio
async def test_api_create_court_forbidden(client, sample_user):
    headers = get_auth_header(sample_user.id)
    payload = {
        "number": 6,
        "surface": "grass",
        "price_per_hour": 50,
        "has_lighting": False,
    }
    response = await client.post("/courts/", json=payload, headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_api_create_duplicate_court_error(client, sample_admin, sample_court):
    headers = get_auth_header(sample_admin.id)
    payload = {
        "number": sample_court.number,
        "surface": "hard",
        "price_per_hour": 25,
        "has_lighting": True,
    }
    response = await client.post("/courts/", json=payload, headers=headers)
    assert response.status_code in [400, 409]


@pytest.mark.asyncio
async def test_api_delete_court_admin(client, sample_admin, sample_court):
    headers = get_auth_header(sample_admin.id)
    response = await client.delete(f"/courts/{sample_court.number}", headers=headers)
    assert response.status_code == 200

    get_res = await client.get(f"/courts/{sample_court.number}")
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_api_get_all_courts(client, sample_court):
    response = await client.get("/courts/all")
    assert response.status_code == 200
    data = response.json()
    assert any(c["number"] == sample_court.number for c in data)


@pytest.mark.asyncio
async def test_api_get_specific_court(client, sample_court):
    response = await client.get(f"/courts/{sample_court.number}")
    assert response.status_code == 200
    assert response.json()["number"] == sample_court.number


@pytest.mark.asyncio
async def test_api_search_courts_by_category(client, session, sample_court):
    c2 = Court(
        number=99,
        surface=Surface.CLAY,
        has_lighting=False,
        price_per_hour=20,
        available=True,
    )
    session.add(c2)
    await session.commit()

    response_hard = await client.get("/courts/?surface=hard")
    data_hard = response_hard.json()

    assert any(c["number"] == sample_court.number for c in data_hard)
    assert not any(c["number"] == 99 for c in data_hard)

    response_lighting = await client.get("/courts/?lighting=false")
    data_lighting = response_lighting.json()

    assert any(c["number"] == 99 for c in data_lighting)
    assert not any(c["number"] == sample_court.number for c in data_lighting)
