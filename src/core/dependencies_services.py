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
    return ReservationService(session)


async def get_user_service(
    session: AsyncSession = Depends(get_async_session),
) -> UserService:
    return UserService(session)


async def get_court_service(
    session: AsyncSession = Depends(get_async_session),
) -> CourtService:
    return CourtService(session)


async def get_loyalty_service(
    session: AsyncSession = Depends(get_async_session),
) -> LoyaltyService:
    return LoyaltyService(session)


async def get_pricing_service(
    session: AsyncSession = Depends(get_async_session),
) -> PricingService:
    return PricingService(session)


async def get_coach_service(
    session: AsyncSession = Depends(get_async_session),
) -> CoachService:
    return CoachService(session)


async def get_review_service(
    session: AsyncSession = Depends(get_async_session),
) -> ReviewService:
    return ReviewService(session)


async def get_favorites_service(
    session: AsyncSession = Depends(get_async_session),
) -> FavoritesService:
    return FavoritesService(session)
