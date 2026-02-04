from datetime import datetime, timedelta
from decimal import Decimal
import pytest
from sqlalchemy import select
from src.models.user import User
from src.models.service import Service, ServiceCategory
from src.models.reservation import Reservation, ReservationStatus
from ..conftest import get_auth_header


@pytest.mark.asyncio
async def test_api_create_service(client, session, sample_coach, sample_service):
    """Test that a coach can create a new service."""
    coach = await session.get(User, sample_coach.id)
    headers = get_auth_header(coach.id)

    payload = sample_service.model_dump(mode="json")

    response = await client.post("/coach/services", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["coach_name"] == coach.full_name
    assert float(data["price"]) == float(payload["price"])


@pytest.mark.asyncio
async def test_api_get_coach_services(client, session, sample_coach, sample_service):
    """Test viewing services created by the logged-in coach."""
    coach = await session.get(User, sample_coach.id)
    headers = get_auth_header(coach.id)
    service = await session.get(Service, sample_service.id)
    service.coach_id = coach.id
    session.add(service)
    await session.commit()

    response = await client.get("/coach/services", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(s["id"] == service.id for s in data)


@pytest.mark.asyncio
async def test_api_get_coach_reservations(
    client, session, sample_coach, sample_service, sample_user
):
    """Test viewing reservations made for the coach's services."""
    coach = await session.get(User, sample_coach.id)
    headers = get_auth_header(coach.id)

    service = await session.get(Service, sample_service.id)
    service.coach_id = coach.id
    session.add(service)

    player = await session.get(User, sample_user.id)

    reservation = Reservation(
        user_id=player.id,
        service_id=service.id,
        court_number=1,
        start_time=datetime.now() + timedelta(days=1),
        end_time=datetime.now() + timedelta(days=1, hours=1),
        price=Decimal("50.00"),
        status=ReservationStatus.CONFIRMED,
    )
    session.add(reservation)
    await session.commit()

    response = await client.get("/coach/reservations", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["service_id"] == service.id
    assert data[0]["user_id"] == player.id


@pytest.mark.asyncio
async def test_api_search_available_services(client, session, sample_coach):
    """Test filtering services by name and category."""
    s1 = Service(
        name="Unique Tennis Lesson",
        price=Decimal("50"),
        duration_minutes=60,
        category=ServiceCategory.INDIVIDUAL,
        coach_id=sample_coach.id,
    )
    s2 = Service(
        name="Cardio Session",
        price=Decimal("30"),
        duration_minutes=45,
        category=ServiceCategory.GROUP,
        coach_id=sample_coach.id,
    )
    session.add_all([s1, s2])
    await session.commit()

    response_name = await client.get("/coach/services/available?name=Unique")
    assert response_name.status_code == 200
    data_name = response_name.json()
    assert len(data_name) == 1
    assert data_name[0]["name"] == "Unique Tennis Lesson"

    response_cat = await client.get(
        f"/coach/services/available?category={ServiceCategory.GROUP.value}"
    )
    assert response_cat.status_code == 200
    data_cat = response_cat.json()
    assert len(data_cat) >= 1
    assert data_cat[0]["category"] == ServiceCategory.GROUP.value
    assert data_cat[0]["name"] == "Cardio Session"


@pytest.mark.asyncio
async def test_api_delete_service(client, session, sample_coach):
    """Test deleting a service."""
    coach = await session.get(User, sample_coach.id)
    headers = get_auth_header(coach.id)

    service_to_delete = Service(
        name="To Be Deleted",
        price=Decimal("10"),
        duration_minutes=30,
        category=ServiceCategory.INDIVIDUAL,
        coach_id=coach.id,
    )
    session.add(service_to_delete)
    await session.commit()
    await session.refresh(service_to_delete)

    service_id = service_to_delete.id

    response = await client.delete(f"/coach/services/{service_id}", headers=headers)

    assert response.status_code == 200

    result = await session.execute(select(Service).where(Service.id == service_id))
    deleted_service = result.scalars().first()

    assert deleted_service is None
