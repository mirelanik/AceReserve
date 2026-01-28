import pytest
from src.models.user import User, Role
from ..conftest import get_auth_header


@pytest.mark.asyncio
async def test_api_create_user(client, session):
    """Test user registration endpoint."""
    payload = {
        "email": "newuser@test.com",
        "password": "password123",
        "full_name": "New User",
    }

    response = await client.post("/users/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "password" not in data
    assert data["full_name"] == payload["full_name"]
    assert data["role"] == "user"
    assert "id" in data

    new_user = await session.get(User, data["id"])
    assert new_user is not None
    assert new_user.role == Role.USER


@pytest.mark.asyncio
async def test_api_login(client, session, sample_user):
    """Test user login"""
    merged_user = await session.merge(sample_user)

    response = await client.post(
        "/users/login",
        data={"username": merged_user.email, "password": "hashed_pwd"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_api_get_current_user(client, session, sample_user):
    """Test retrieving current authenticated user"""
    merged_user = await session.merge(sample_user)

    response = await client.get("/users/me", headers=get_auth_header(merged_user.id))

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == merged_user.email
    assert data["full_name"] == merged_user.full_name
    assert data["role"] == merged_user.role.value
    assert data["id"] == merged_user.id


@pytest.mark.asyncio
async def test_api_create_user_by_admin(client, session, sample_admin):
    """Test admin creating a new user"""
    merged_admin = await session.merge(sample_admin)
    headers = get_auth_header(merged_admin.id)
    payload = {
        "email": "newuser@example.com",
        "password": "password123",
        "full_name": "New User",
    }

    response = await client.post(
        "/users/create-by-admin",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["role"] == "user"
    assert "id" in data

    db_user = await session.get(User, data["id"])
    assert db_user is not None


@pytest.mark.asyncio
async def test_api_create_user_by_non_admin(client, session, sample_user):
    """Test non-admin user trying to create a new user"""
    merged_user = await session.merge(sample_user)
    headers = get_auth_header(merged_user.id)
    payload = {
        "email": "newuser@example.com",
        "password": "password123",
        "full_name": "New User",
    }
    response = await client.post(
        "/users/create-by-admin",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_api_remove_user_by_admin(client, session, sample_admin, sample_user):
    """Test admin deleting an existing user"""
    merged_admin = await session.merge(sample_admin)
    merged_user = await session.merge(sample_user)
    headers = get_auth_header(merged_admin.id)

    user_id_to_delete = merged_user.id
    response = await client.delete(
        f"/users/{user_id_to_delete}",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "msg" in data

    session.expire_all()
    deleted_user = await session.get(User, user_id_to_delete)
    assert deleted_user is None
