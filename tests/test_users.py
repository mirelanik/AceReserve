import pytest
from datetime import datetime, timedelta, timezone
from sqlmodel import col
from src.auth.security import create_access_token
from src.models.user import User, Role
from sqlalchemy import select
from src.services.user_service import UserService
from src.models.user import User, UserCreate, Role
from src.models.reservation import ReservationCreate, Reservation, ReservationStatus
from src.services.reservation_service import ReservationService
from src.core.exceptions import ExistingUserError, UserNotFoundError


@pytest.mark.asyncio
async def test_create_user(client, session):
    """Test user creation"""
    response = await client.post(
        "/users/register",
        json={
            "email": "newuser@test.com",
            "password": "password123",
            "full_name": "New User",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert "password" not in data
    assert data["full_name"] == "New User"
    assert data["role"] == "user"
    assert "id" in data

    new_user = await session.get(User, data["id"])
    assert new_user is not None
    assert new_user.role == Role.USER


@pytest.mark.asyncio
async def test_login(client):
    """Test user login"""

    registration_response = await client.post(
        "/users/register",
        json={
            "email": "loginuser@test.com",
            "password": "password123",
            "full_name": "Login User",
        },
    )
    assert registration_response.status_code == 201

    response = await client.post(
        "/users/login",
        data={"username": "loginuser@test.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_current_user(client, sample_user):
    """Test retrieving current authenticated user"""

    token = create_access_token(data={"sub": str(sample_user.id)})

    response = await client.get(
        "/users/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_user.email
    assert data["full_name"] == sample_user.full_name
    assert data["role"] == sample_user.role.value
    assert data["id"] == sample_user.id


@pytest.mark.asyncio
async def test_create_user_duplicate_email(session, sample_user):
    """Test creating a user with duplicate email raises error."""
    merged_user = await session.merge(sample_user)

    service = UserService(session)
    user_input = UserCreate(
        email=merged_user.email,
        password="password123",
        full_name="Another User",
    )

    with pytest.raises(ExistingUserError):
        await service.create_user(user_input)


@pytest.mark.asyncio
async def test_authenticate_user_success(session):
    """Test successful user authentication."""
    service = UserService(session)
    user_input = UserCreate(
        email="authuser@example.com",
        password="password123",
        full_name="Auth User",
    )

    created_user = await service.create_user(user_input)

    authenticated_user = await service.authenticate_user(
        "authuser@example.com", "password123"
    )

    assert authenticated_user is not None
    assert authenticated_user.id == created_user.id
    assert authenticated_user.email == created_user.email


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(session, sample_user):
    """Test authentication with wrong password."""
    merged_user = await session.merge(sample_user)
    service = UserService(session)

    authenticated_user = await service.authenticate_user(
        merged_user.email, "wrongpassword"
    )

    assert authenticated_user is None


@pytest.mark.asyncio
async def test_authenticate_user_nonexistent(session):
    """Test authentication with non-existent user."""
    service = UserService(session)

    authenticated_user = await service.authenticate_user(
        "nonexistent@example.com", "password"
    )

    assert authenticated_user is None


@pytest.mark.asyncio
async def test_create_user_by_admin_coach(session, sample_admin):
    """Test admin creating a coach user."""
    merged_user = await session.merge(sample_admin)
    service = UserService(session)
    user_input = UserCreate(
        email="newcoach@example.com",
        password="password123",
        full_name="New Coach",
    )

    coach = await service.create_user_by_admin(user_input, Role.COACH, merged_user)

    assert coach.email == "newcoach@example.com"
    assert coach.role == Role.COACH

    stored_user = await session.get(User, coach.id)
    assert stored_user is not None
    assert stored_user.role == Role.COACH


@pytest.mark.asyncio
async def test_create_user_by_admin_admin(session, sample_admin):
    """Test admin creating another admin user."""
    merged_user = await session.merge(sample_admin)
    service = UserService(session)
    user_input = UserCreate(
        email="newadmin@example.com",
        password="password123",
        full_name="New Admin",
    )

    admin = await service.create_user_by_admin(user_input, Role.ADMIN, merged_user)

    assert admin.email == "newadmin@example.com"
    assert admin.role == Role.ADMIN

    stored_user = await session.get(User, admin.id)
    assert stored_user is not None
    assert stored_user.role == Role.ADMIN


@pytest.mark.asyncio
async def test_remove_user_by_admin(session, sample_user):
    """Test admin removing a user."""
    merged_user = await session.merge(sample_user)
    service = UserService(session)

    result = await service.remove_user_by_admin(merged_user.id)

    assert result["msg"] == "User deleted successfully"

    deleted_user = await session.get(User, merged_user.id)
    assert deleted_user is None


@pytest.mark.asyncio
async def test_remove_nonexistent_user_by_admin(session):
    """Test removing non-existent user raises error."""
    service = UserService(session)

    with pytest.raises(UserNotFoundError):
        await service.remove_user_by_admin(999)


@pytest.mark.asyncio
async def test_remove_user_cancels_reservations(session, sample_user, sample_court):
    """Test that removing a user cancels their reservations."""

    merged_user = await session.merge(sample_user)
    merged_court = await session.merge(sample_court)

    res_service = ReservationService(session)
    start_time = datetime.now(timezone.utc) + timedelta(days=5)
    res_input = ReservationCreate(
        court_number=merged_court.number,
        start_time=start_time,
        duration_minutes=60,
    )
    reservation = await res_service.process_reservation_creation(merged_user, res_input)

    user_service = UserService(session)
    await user_service.remove_user_by_admin(merged_user.id)

    cancelled_reservation = await session.get(Reservation, reservation.id)
    assert cancelled_reservation is not None
    assert cancelled_reservation.status == ReservationStatus.CANCELLED


@pytest.mark.asyncio
async def test_loyalty_account_created_with_user(session):
    """Test that loyalty account is created when user is created."""
    from src.models.loyalty import LoyaltyAccount

    service = UserService(session)
    user_input = UserCreate(
        email="loyaltyuser@example.com",
        password="password123",
        full_name="Loyalty User",
    )

    user = await service.create_user(user_input)

    statement = select(LoyaltyAccount).where(col(LoyaltyAccount.user_id) == user.id)
    result = await session.execute(statement)
    loyalty = result.scalars().first()

    assert loyalty is not None
    assert loyalty.user_id == user.id
    assert loyalty.points == 0
