from datetime import datetime, timedelta, timezone
import pytest
from src.models.reservation import ReservationCreate, ReservationStatus
from src.services.reservation_service import ReservationService
from ..conftest import get_auth_header


@pytest.mark.asyncio
async def test_api_create_reservation(client, session, sample_user, sample_court):
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    start_time = datetime.now(timezone.utc).replace(hour=12, minute=0) + timedelta(
        days=1
    )

    payload = {
        "court_number": merged_court.number,
        "start_time": start_time.isoformat(),
        "duration_minutes": 60,
        "wants_lighting": False,
        "rent_racket": True,
        "rent_balls": False,
    }

    headers = get_auth_header(merged_user.id)

    response = await client.post("/reservations/", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["court_number"] == merged_court.number
    assert data["user_id"] == merged_user.id
    assert data["rent_racket"] is True
    assert "id" in data
    assert data["start_time"].startswith(start_time.isoformat().split(".")[0])


@pytest.mark.asyncio
async def test_api_create_reservation_unauthorized(client, sample_court):
    start_time = datetime.now(timezone.utc).replace(hour=12, minute=0) + timedelta(
        days=1
    )
    payload = {
        "court_number": sample_court.number,
        "start_time": start_time.isoformat(),
        "duration_minutes": 60,
    }

    response = await client.post("/reservations/", json=payload)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_api_create_reservation_validation_error(
    client, session, sample_user, sample_court
):
    merged_user = await session.merge(sample_user)
    headers = get_auth_header(merged_user.id)

    payload = {"court_number": sample_court.number, "duration_minutes": "not-a-number"}

    response = await client.post("/reservations/", json=payload, headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_api_get_my_reservations(client, session, sample_user, sample_court):
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    service = ReservationService(session)
    start_time = datetime.now(timezone.utc).replace(hour=12, minute=0) + timedelta(
        days=1
    )
    create_data = ReservationCreate(
        court_number=merged_court.number, start_time=start_time, duration_minutes=60
    )
    await service.process_reservation_creation(merged_user, create_data)

    headers = get_auth_header(merged_user.id)
    response = await client.get("/reservations/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(res["court_number"] == merged_court.number for res in data)


@pytest.mark.asyncio
async def test_api_cancel_reservation(client, session, sample_user, sample_court):
    """Test PATCH /reservations/{id} - Отказване на резервация."""
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    service = ReservationService(session)
    start_time = datetime.now(timezone.utc).replace(hour=12, minute=0) + timedelta(
        days=2
    )
    res = await service.process_reservation_creation(
        merged_user,
        ReservationCreate(
            court_number=merged_court.number, start_time=start_time, duration_minutes=60
        ),
    )

    headers = get_auth_header(merged_user.id)
    response = await client.patch(f"/reservations/{res.id}", headers=headers)

    assert response.status_code == 200
    await session.refresh(res)
    assert res.status == ReservationStatus.CANCELLED


@pytest.mark.asyncio
async def test_api_edit_reservation(client, session, sample_user, sample_court):
    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    service = ReservationService(session)
    start_time = datetime.now(timezone.utc).replace(hour=12, minute=0) + timedelta(
        days=3
    )
    reservation = await service.process_reservation_creation(
        merged_user,
        ReservationCreate(
            court_number=merged_court.number, start_time=start_time, duration_minutes=60
        ),
    )

    new_start_time = start_time + timedelta(hours=1)
    update_payload = {"start_time": new_start_time.isoformat(), "duration_minutes": 90}
    headers = get_auth_header(merged_user.id)
    response = await client.put(
        f"/reservations/{reservation.id}", json=update_payload, headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["duration_minutes"] == 90

    await session.refresh(reservation)
    assert reservation.duration_minutes == 90


@pytest.mark.asyncio
async def test_api_cancel_others_reservation_forbidden(
    client, session, sample_user, sample_user_other, sample_court
):
    merged_attacker = await session.merge(sample_user)
    merged_victim = await session.merge(sample_user_other)
    merged_court = await session.merge(sample_court)

    service = ReservationService(session)
    start_time = datetime.now(timezone.utc).replace(hour=12, minute=0) + timedelta(
        days=4
    )
    reservation = await service.process_reservation_creation(
        merged_victim,
        ReservationCreate(
            court_number=merged_court.number, start_time=start_time, duration_minutes=60
        ),
    )

    headers = get_auth_header(merged_attacker.id)
    response = await client.patch(f"/reservations/{reservation.id}", headers=headers)

    assert response.status_code == 403
