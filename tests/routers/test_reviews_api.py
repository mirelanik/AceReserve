import pytest
from src.models.user import User
from ..conftest import get_auth_header
from src.models.review import ReviewCreate, ReviewTargetType


@pytest.fixture
async def sample_review_court(sample_court):
    """Create a test review."""
    return ReviewCreate(
        rating=5,
        comment="Great court!",
        target_type=ReviewTargetType.COURT,
        court_number=sample_court.number,
    )


@pytest.fixture
async def sample_review_coach(sample_coach):
    """Create a test review."""
    return ReviewCreate(
        rating=5,
        comment="Excellent coach!",
        target_type=ReviewTargetType.COACH,
        coach_id=sample_coach.id,
    )


@pytest.fixture
async def sample_review_service(sample_service):
    """Create a test review."""
    return ReviewCreate(
        rating=4,
        comment="Good but not great",
        target_type=ReviewTargetType.SERVICE,
        service_id=sample_service.id,
    )


@pytest.mark.asyncio
async def test_api_create_review_court(
    client, session, sample_user, sample_review_court
):
    """Test creating a review for a court."""
    current_user = await session.get(User, sample_user.id)

    headers = get_auth_header(current_user.id)
    payload = sample_review_court.model_dump()
    response = await client.post(
        "/reviews/",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == payload["rating"]
    assert data["comment"] == payload["comment"]
    assert data["target_type"] == payload["target_type"]
    assert data["court_number"] == payload["court_number"]


@pytest.mark.asyncio
async def test_api_create_review_coach(
    client, session, sample_user, sample_review_coach
):
    """Test creating a review for a coach."""
    current_user = await session.get(User, sample_user.id)

    headers = get_auth_header(current_user.id)
    payload = sample_review_coach.model_dump()
    response = await client.post(
        "/reviews/",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == payload["rating"]
    assert data["comment"] == payload["comment"]
    assert data["target_type"] == payload["target_type"]
    assert data["coach_id"] == payload["coach_id"]


@pytest.mark.asyncio
async def test_api_get_reviews_for_court(
    client, session, sample_court, sample_review_court, sample_user
):
    """Test showing reviews for a specific court."""
    current_user = await session.get(User, sample_user.id)
    headers = get_auth_header(current_user.id)
    payload = sample_review_court.model_dump()
    await client.post(
        "/reviews/",
        json=payload,
        headers=headers,
    )

    response = await client.get(
        f"/reviews/court/{sample_court.number}", headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(review["court_number"] == sample_court.number for review in data)


@pytest.mark.asyncio
async def test_api_get_reviews_for_coach(
    client, session, sample_coach, sample_review_coach, sample_user
):
    """Test showing reviews for a specific coach."""
    current_user = await session.get(User, sample_user.id)
    headers = get_auth_header(current_user.id)
    payload = sample_review_coach.model_dump()
    await client.post(
        "/reviews/",
        json=payload,
        headers=headers,
    )

    response = await client.get(f"/reviews/coach/{sample_coach.id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(review["coach_id"] == sample_coach.id for review in data)


@pytest.mark.asyncio
async def test_api_get_reviews_for_service(
    client, session, sample_service, sample_review_service, sample_user
):
    """Test showing reviews for a specific court."""
    current_user = await session.get(User, sample_user.id)
    headers = get_auth_header(current_user.id)
    payload = sample_review_service.model_dump()
    await client.post(
        "/reviews/",
        json=payload,
        headers=headers,
    )

    response = await client.get(
        f"/reviews/service/{sample_service.id}", headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(review["service_id"] == sample_service.id for review in data)


@pytest.mark.asyncio
async def test_api_get_average_rating_calculation(
    client, session, sample_user, sample_user_other, sample_review_court, sample_court
):
    """Test calculating average rating with multiple reviews."""
    user1 = await session.get(User, sample_user.id)
    headers1 = get_auth_header(user1.id)
    user2 = await session.get(User, sample_user_other.id)
    headers2 = get_auth_header(user2.id)

    payload1 = sample_review_court.model_dump()
    await client.post("/reviews/", json=payload1, headers=headers1)

    payload2 = {
        "rating": 3,
        "comment": "It was okay.",
        "target_type": ReviewTargetType.COURT.value,
        "court_number": sample_court.number,
    }
    await client.post("/reviews/", json=payload2, headers=headers2)

    params = {"court_number": sample_court.number}
    response = await client.get(
        "/reviews/average-rating", params=params, headers=headers1
    )

    assert response.status_code == 200
    data = response.json()
    assert data["average_rating"] == 4.0
