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
    """Get ReservationService instance with database session.
    Args:
        session: Database session from async_database module.
    Returns:
        ReservationService: Service instance ready for use.
    """
    return ReservationService(session)


async def get_user_service(
    session: AsyncSession = Depends(get_async_session),
) -> UserService:
    """Get UserService instance with database session.
    Args:
        session: Database session from async_database module.
    Returns:
        UserService: Service instance ready for use.
    """
    return UserService(session)


async def get_court_service(
    session: AsyncSession = Depends(get_async_session),
) -> CourtService:
    """Get CourtService instance with database session.
    Args:
        session: Database session from async_database module.
    Returns:
        CourtService: Service instance ready for use.
    """
    return CourtService(session)


async def get_loyalty_service(
    session: AsyncSession = Depends(get_async_session),
) -> LoyaltyService:
    """Get LoyaltyService instance with database session.
    Args:
        session: Database session from async_database module.
    Returns:
        LoyaltyService: Service instance ready for use.
    """
    return LoyaltyService(session)


async def get_pricing_service(
    session: AsyncSession = Depends(get_async_session),
) -> PricingService:
    """Get PricingService instance with database session.
    Args:
        session: Database session from async_database module.
    Returns:
        PricingService: Service instance ready for use.
    """
    return PricingService(session)


async def get_coach_service(
    session: AsyncSession = Depends(get_async_session),
) -> CoachService:
    """Get CoachService instance with database session.
    Args:
        session: Database session from async_database module.
    Returns:
        CoachService: Service instance ready for use.
    """
    return CoachService(session)


async def get_review_service(
    session: AsyncSession = Depends(get_async_session),
) -> ReviewService:
    """Get ReviewService instance with database session.
    Args:
        session: Database session from async_database module.
    Returns:
        ReviewService: Service instance ready for use.
    """
    return ReviewService(session)


async def get_favorites_service(
    session: AsyncSession = Depends(get_async_session),
) -> FavoritesService:
    """Get FavoritesService instance with database session.
    Args:
        session: Database session from async_database module.
    Returns:
        FavoritesService: Service instance ready for use.
    """
    return FavoritesService(session)
