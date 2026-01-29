import pytest
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from src.services.coach_service import CoachService
from src.models.service import ServiceCreate, ServiceCategory, Service
from src.models.reservation import Reservation, ReservationStatus
from src.models.user import Role, User
from src.core.exceptions import (
    CoachNotFoundError,
    ServiceNotFoundError,
)


@pytest.fixture
async def sample_service_data():
    return ServiceCreate(
        name="Advanced Tennis",
        description="Pro level training",
        price=Decimal("80.00"),
        duration_minutes=60,
        category=ServiceCategory.INDIVIDUAL,
    )


@pytest.mark.asyncio
async def test_create_service_by_coach(session, sample_coach, sample_service_data):
    """Test coach creating their own service."""
    service_logic = CoachService(session)
    merged_coach = await session.merge(sample_coach)

    service = await service_logic.create_new_service(merged_coach, sample_service_data)

    assert service.id is not None
    assert service.coach_id == merged_coach.id
    assert service.requires_coach is True
    assert service.name == "Advanced Tennis"


@pytest.mark.asyncio
async def test_create_service_by_admin(
    session, sample_admin, sample_coach, sample_service_data
):
    """Test admin creating a service for a coach."""
    service_logic = CoachService(session)
    merged_admin = await session.merge(sample_admin)
    merged_coach = await session.merge(sample_coach)
    
    sample_service_data.coach_id = merged_coach.id
    service = await service_logic.create_new_service(merged_admin, sample_service_data)

    assert service.coach_id == merged_coach.id
    assert service.price == Decimal("80.00")


@pytest.mark.asyncio
async def test_create_service_invalid_coach(
    session, sample_admin, sample_service_data
):
    """Test admin trying to assign service to non-coach user."""
    service_logic = CoachService(session)
    merged_admin = await session.merge(sample_admin)

    regular_user = User(
        email="user@test.com", full_name="User", hashed_password="pwd", role=Role.USER
    )
    session.add(regular_user)
    await session.commit()

    sample_service_data.coach_id = regular_user.id

    with pytest.raises(CoachNotFoundError):
        await service_logic.create_new_service(merged_admin, sample_service_data)


@pytest.mark.asyncio
async def test_get_services_by_coach(session, sample_coach, sample_service_data):
    """Test retrieving services for a specific coach."""
    service_logic = CoachService(session)
    merged_coach = await session.merge(sample_coach)

    await service_logic.create_new_service(merged_coach, sample_service_data)
    await session.refresh(merged_coach, ["services"])
    services = service_logic.get_services_by_coach(merged_coach)

    assert len(services) == 1
    assert services[0].name == sample_service_data.name


@pytest.mark.asyncio
async def test_get_reservations_for_coach(
    session, sample_coach, sample_user, sample_service_data
):
    """Test getting reservations for services owned by the coach."""
    service_logic = CoachService(session)
    merged_coach = await session.merge(sample_coach)
    merged_user = await session.merge(sample_user)

    service = await service_logic.create_new_service(merged_coach, sample_service_data)

    reservation = Reservation(
        user_id=merged_user.id,
        service_id=service.id,
        court_number=1,
        start_time=datetime.now(timezone.utc) + timedelta(days=1),
        duration_minutes=60,
        end_time=datetime.now(timezone.utc) + timedelta(days=1, minutes=60),
        total_price=Decimal("100.00"),
        status=ReservationStatus.PENDING,
    )
    session.add(reservation)
    await session.commit()
    await session.refresh(merged_coach, ["services"])
    reservations = await service_logic.get_reservations_for_coach(merged_coach)

    assert len(reservations) == 1
    assert reservations[0].id == reservation.id


@pytest.mark.asyncio
async def test_select_available_services_filter(session, sample_coach):
    """Test filtering services by name and availability."""
    service_logic = CoachService(session)

    s1 = Service(
        name="Professional Training",
        coach_id=sample_coach.id,
        price=Decimal("10.00"),
        duration_minutes=60,
        is_available=True,
    )
    s2 = Service(
        name="Children Lesson",
        coach_id=sample_coach.id,
        price=Decimal("10.00"),
        duration_minutes=60,
        is_available=True,
    )

    s3 = Service(
        name="Individual training",
        coach_id=sample_coach.id,
        price=Decimal("10.00"),
        duration_minutes=60,
        is_available=False,
    )

    session.add_all([s1, s2, s3])
    await session.commit()

    results = await service_logic.select_available_services(name="Professional Training")
    assert len(results) == 1
    assert results[0].name == "Professional Training"

    results_all = await service_logic.select_available_services()
    assert len(results_all) == 2
    names = [s.name for s in results_all]
    assert "Individual training" not in names


@pytest.mark.asyncio
async def test_remove_service(session, sample_coach, sample_service_data):
    """Test deleting a service."""
    service_logic = CoachService(session)
    merged_coach = await session.merge(sample_coach)

    service = await service_logic.create_new_service(merged_coach, sample_service_data)
    service_id = service.id

    assert service_id is not None

    response = await service_logic.remove_service(service_id, merged_coach)
    assert response["msg"] == "Service deleted successfully"

    deleted_service = await session.get(Service, service_id)
    assert deleted_service is None


@pytest.mark.asyncio
async def test_remove_nonexistent_service(session, sample_coach):
    """Test deleting a service that doesn't exist."""
    service_logic = CoachService(session)
    merged_coach = await session.merge(sample_coach)

    with pytest.raises(ServiceNotFoundError):
        await service_logic.remove_service(999, merged_coach)
