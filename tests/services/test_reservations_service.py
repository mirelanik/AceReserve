from decimal import Decimal
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import select
from src.models.reservation import (
    ReservationCreate,
    ReservationStatus,
    ReservationUpdate,
)
from src.models.loyalty import LoyaltyAccount, LoyaltyLevel
from src.models.service import Service
from src.services.reservation_service import ReservationService
from src.core.exceptions import (
    DoubleCourtBookingError,
    LightingTimeError,
    ForbiddenActionError,
    StartTimeError,
    ClubNotOpenError,
    ClubClosedError
)


@pytest.mark.asyncio
async def test_prevent_court_double_booking(session, sample_user, sample_court):
    service = ReservationService(session)
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    data = ReservationCreate(
        court_number=merged_court.number, start_time=start_time, duration_minutes=60
    )

    await service.process_reservation_creation(merged_user, data)

    with pytest.raises(DoubleCourtBookingError):
        await service.process_reservation_creation(merged_user, data)


@pytest.mark.asyncio
async def test_no_lighting_before_19h(session, sample_user, sample_court):
    service = ReservationService(session)
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    start_time = datetime.now(timezone.utc).replace(hour=14, minute=0) + timedelta(
        days=1
    )
    data = ReservationCreate(
        court_number=merged_court.number,
        start_time=start_time,
        duration_minutes=60,
        wants_lighting=True,
    )

    with pytest.raises(LightingTimeError):
        await service.process_reservation_creation(merged_user, data)


@pytest.mark.asyncio
async def test_reservation_updates_loyalty_points(session, sample_user, sample_court):
    service = ReservationService(session)
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    statement = select(LoyaltyAccount).where(LoyaltyAccount.user_id == merged_user.id)
    result = await session.execute(statement)
    loyalty_account = result.scalars().first()

    if not loyalty_account:
        loyalty_account = LoyaltyAccount(
            user_id=merged_user.id, points=0, level=LoyaltyLevel.BEGINNER
        )
        session.add(loyalty_account)
        await session.commit()
        await session.refresh(loyalty_account)

    initial_points = loyalty_account.points

    start_time = datetime.now(timezone.utc) + timedelta(days=2)
    data = ReservationCreate(
        court_number=merged_court.number,
        start_time=start_time,
        duration_minutes=60,
    )

    await service.process_reservation_creation(merged_user, data)

    result = await session.execute(statement)
    updated_loyalty = result.scalars().first()

    assert updated_loyalty is not None
    assert updated_loyalty.points == initial_points + 10


@pytest.mark.asyncio
async def test_get_user_reservations(
    session, sample_user, sample_user_other, sample_court
):
    service = ReservationService(session)
    merged_user = await session.merge(sample_user)
    merged_user_other = await session.merge(sample_user_other)
    merged_court = await session.merge(sample_court)

    base_time = datetime.now(timezone.utc) + timedelta(days=1)

    for i in range(2):
        await service.process_reservation_creation(
            merged_user,
            ReservationCreate(
                court_number=merged_court.number,
                start_time=base_time + timedelta(hours=i),
                duration_minutes=60,
            ),
        )

    await service.process_reservation_creation(
        merged_user_other,
        ReservationCreate(
            court_number=merged_court.number,
            start_time=base_time + timedelta(hours=5),
            duration_minutes=60,
        ),
    )

    reservations = await service.get_user_reservations(merged_user)
    assert len(reservations) == 2
    assert all(res.user_id == merged_user.id for res in reservations)


@pytest.mark.asyncio
async def test_delete_reservation(session, sample_user, sample_court):
    service = ReservationService(session)
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    reservation_data = ReservationCreate(
        court_number=merged_court.number, start_time=start_time, duration_minutes=60
    )
    reservation = await service.process_reservation_creation(
        merged_user, reservation_data
    )
    assert reservation.id is not None
    response = await service.delete_reservation(merged_user, reservation.id)

    await session.refresh(reservation)
    assert reservation.status == ReservationStatus.CANCELLED
    assert response["message"] == "Reservation was cancelled successfully."


@pytest.mark.asyncio
async def test_delete_reservation_forbidden(
    session, sample_user, sample_user_other, sample_court
):
    service = ReservationService(session)
    merged_user = await session.merge(sample_user)
    merged_owner = await session.merge(sample_user_other)
    merged_court = await session.merge(sample_court)

    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    reservation = await service.process_reservation_creation(
        merged_owner,
        ReservationCreate(
            court_number=merged_court.number, start_time=start_time, duration_minutes=60
        ),
    )

    assert reservation.id is not None
    with pytest.raises(ForbiddenActionError):
        await service.delete_reservation(merged_user, reservation.id)


@pytest.mark.asyncio
async def test_modify_reservation(session, sample_user, sample_court):
    """Test modifying an existing reservation."""
    service = ReservationService(session)
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    start_time = datetime.now(timezone.utc) + timedelta(days=2)
    create_data = ReservationCreate(
        court_number=merged_court.number,
        start_time=start_time,
        duration_minutes=60,
    )
    reservation = await service.process_reservation_creation(merged_user, create_data)
    assert reservation.id is not None

    new_start_time = datetime.now(timezone.utc) + timedelta(days=3)
    modify_data = ReservationUpdate(
        start_time=new_start_time,
        duration_minutes=90,
    )

    modified_reservation = await service.modify_reservation(
        merged_user, reservation.id, modify_data
    )

    res_time = modified_reservation.start_time.replace(tzinfo=None)
    target_time = new_start_time.replace(tzinfo=None)

    assert modified_reservation.duration_minutes == 90
    assert abs((res_time - target_time).total_seconds()) < 1


@pytest.mark.asyncio
async def test_prevent_past_reservation(session, sample_user, sample_court):
    """Test that reservations cannot be made in the past."""
    service = ReservationService(session)
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    start_time = datetime.now(timezone.utc) - timedelta(days=1)
    data = ReservationCreate(
        court_number=merged_court.number,
        start_time=start_time,
        duration_minutes=60,
    )

    with pytest.raises(StartTimeError):
        await service.process_reservation_creation(merged_user, data)


@pytest.mark.asyncio
async def test_reservation_with_service(session, sample_user, sample_court):
    """Test creating a reservation with additional service."""
    service = ReservationService(session)
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    service_obj = Service(
        name="Ball Rental",
        court_number=merged_court.number,
        price=Decimal("10.00"),
        duration_minutes=60,
    )
    session.add(service_obj)
    await session.commit()
    await session.refresh(service_obj)

    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    data = ReservationCreate(
        court_number=merged_court.number,
        start_time=start_time,
        duration_minutes=60,
        service_id=service_obj.id,
    )

    reservation = await service.process_reservation_creation(merged_user, data)

    assert reservation.service_id == service_obj.id


@pytest.mark.asyncio
async def test_reservation_with_racket_and_balls_rental(
    session, sample_user, sample_court
):
    """Test creating a reservation with racket and balls rental."""
    service = ReservationService(session)
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    data = ReservationCreate(
        court_number=merged_court.number,
        start_time=start_time,
        duration_minutes=60,
        rent_racket=True,
        rent_balls=True,
    )

    reservation = await service.process_reservation_creation(merged_user, data)

    assert reservation.rent_racket is True
    assert reservation.rent_balls is True


@pytest.mark.asyncio
async def test_create_reservation_outside_hours(session, sample_user, sample_court):
    service = ReservationService(session)
    merged_court = await session.merge(sample_court)
    base_time = datetime.now(timezone.utc)

    early_start = base_time.replace(
        hour=6, minute=0, second=0, microsecond=0
    ) + timedelta(days=1)
    
    reservation_early = ReservationCreate(
        court_number=merged_court.number,
        start_time=early_start,
    )

    with pytest.raises(ClubNotOpenError) as excinfo:
        await service.process_reservation_creation(sample_user, reservation_early)

    assert excinfo.value.status_code == 400
    assert "Club opens" in excinfo.value.detail

    late_start = base_time.replace(
        hour=23, minute=0, second=0, microsecond=0
    ) + timedelta(days=1)

    reservation_late = ReservationCreate(
        court_number=merged_court.number,
        start_time=late_start,
    )

    with pytest.raises(ClubClosedError) as excinfo:
        await service.process_reservation_creation(sample_user, reservation_late)

    assert excinfo.value.status_code == 400
    assert "Club closes" in excinfo.value.detail
