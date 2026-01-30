import pytest
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.core.async_database import DatabaseService, get_async_session
from src.auth.security import create_access_token
from src.models.user import User, Role
from src.models.loyalty import LoyaltyAccount, LoyaltyLevel
from src.models.court import Court, Surface
from src.models.service import Service
from src.auth.hashing import get_password_hash

pytest_plugins = ("pytest_asyncio",)


def pytest_configure(config):
    config.option.asyncio_mode = "auto"


@pytest.fixture
async def test_db():
    """Create an in-memory database for testing with automatic cleanup"""
    db = DatabaseService("sqlite+aiosqlite:///:memory:")
    await db.create_tables()
    yield db
    await db.drop_tables()
    await db.close()


@pytest.fixture
async def session(test_db):
    """
    Creates a new database session for a test.
    This allows tests to request 'session' as an argument.
    """
    async with test_db.async_session() as session:
        yield session


@pytest.fixture
async def client(test_db: DatabaseService):
    """Create FastAPI test client with test database"""

    async def override_get_async_session():
        async with test_db.async_session() as session:
            yield session

    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def sample_user(session):
    """Create a test user"""
    user = User(
        email="user@test.com",
        hashed_password=get_password_hash("hashed_pwd"),
        full_name="Test User",
        role=Role.USER,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    loyalty = LoyaltyAccount(user_id=user.id, points=0, level=LoyaltyLevel.BEGINNER)
    session.add(loyalty)
    await session.commit()

    return user


@pytest.fixture
async def sample_user_other(session):
    """Create a second user with loyalty account for testing conflicts."""
    user = User(
        email="other@example.com",
        full_name="Other User",
        hashed_password=get_password_hash("password123"),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    loyalty = LoyaltyAccount(user_id=user.id, points=0, level=LoyaltyLevel.BEGINNER)
    session.add(loyalty)
    await session.commit()

    return user


@pytest.fixture
async def sample_coach(session):
    """Create a test coach user"""
    coach = User(
        email="coach@test.com",
        full_name="Coach User",
        hashed_password=get_password_hash("hashed_pwd"),
        role=Role.COACH,
    )
    session.add(coach)
    await session.commit()
    await session.refresh(coach)

    return coach


@pytest.fixture
async def sample_admin(session):
    """Create a test admin user"""
    admin = User(
        email="admin@test.com",
        hashed_password=get_password_hash("admin_pwd"),
        full_name="Admin",
        role=Role.ADMIN,
    )
    session.add(admin)
    await session.commit()
    await session.refresh(admin)

    return admin


@pytest.fixture
async def sample_court(session):
    """Create a test court"""
    court = Court(
        number=1,
        surface=Surface.HARD,
        price_per_hour=Decimal("25.00"),
        has_lighting=True,
        available=True,
    )
    session.add(court)
    await session.commit()
    await session.refresh(court)

    return court


@pytest.fixture
async def sample_service(session):
    """Create a test service."""
    service = Service(
        name="Tennis Lessons",
        price=Decimal("50.00"),
        duration_minutes=60,
    )
    session.add(service)
    await session.commit()
    await session.refresh(service)
    return service

def get_auth_header(user_id: int):
    """Generate JWT auth header for testing"""
    token = create_access_token(data={"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}
