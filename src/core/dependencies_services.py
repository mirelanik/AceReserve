"""Dependency injection functions for service instances with database sessions."""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from ..core.async_database import get_async_session
from ..services.reservation_service import ReservationService
from ..services.user_service import UserService
from ..services.court_service import CourtService
from ..services.loyalty_service import LoyaltyService
from ..services.pricing_service import PricingService
from ..services.coach_service import CoachService
from ..services.review_service import ReviewService
from ..services.favorites_services import FavoritesService


async def get_reservation_service(
    session: AsyncSession = Depends(get_async_session),
) -> ReservationService:
    """Get a ReservationService instance with an async database session."""
    return ReservationService(session)


async def get_user_service(
    session: AsyncSession = Depends(get_async_session),
) -> UserService:
    """Get a UserService instance with an async database session."""
    return UserService(session)


async def get_court_service(
    session: AsyncSession = Depends(get_async_session),
) -> CourtService:
    """Get a CourtService instance with an async database session."""
    return CourtService(session)


async def get_loyalty_service(
    session: AsyncSession = Depends(get_async_session),
) -> LoyaltyService:
    """Get a LoyaltyService instance with an async database session."""
    return LoyaltyService(session)


async def get_pricing_service(
    session: AsyncSession = Depends(get_async_session),
) -> PricingService:
    """Get a PricingService instance with an async database session."""
    return PricingService(session)


async def get_coach_service(
    session: AsyncSession = Depends(get_async_session),
) -> CoachService:
    """Get a CoachService instance with an async database session."""
    return CoachService(session)


async def get_review_service(
    session: AsyncSession = Depends(get_async_session),
) -> ReviewService:
    """Get a ReviewService instance with an async database session."""
    return ReviewService(session)


async def get_favorites_service(
    session: AsyncSession = Depends(get_async_session),
) -> FavoritesService:
    """Get a FavoritesService instance with an async database session."""
    return FavoritesService(session)
