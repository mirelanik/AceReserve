"""Favorite management API endpoints.
Handles adding/removing courts and coaches from user favorites.
"""

from fastapi import APIRouter, Depends
from ..models.user import User
from ..core.dependencies_services import get_favorites_service
from ..services.favorites_services import FavoritesService
from ..auth.dependencies import require_user

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post("/courts/{court_number}")
async def add_court_favorite(
    court_number: int,
    current_user: User = Depends(require_user),
    service: FavoritesService = Depends(get_favorites_service),
):
    """Add a court to user's favorite courts.
    Args:
        court_number: The court number to add.
        current_user: The authenticated user.
        service: FavoritesService instance.
    Returns:
        dict: Success message.
    """
    return await service.add_court_to_favorites(current_user, court_number)


@router.delete("/courts/{court_number}")
async def remove_court_favorite(
    court_number: int,
    current_user: User = Depends(require_user),
    service: FavoritesService = Depends(get_favorites_service),
):
    """Remove a court from user's favorite courts.
    Args:
        court_number: The court number to remove.
        current_user: The authenticated user.
        service: FavoritesService instance.
    Returns:
        dict: Success message.
    """
    return await service.remove_court_from_favorites(current_user, court_number)


@router.get("/courts")
async def get_favorite_courts(
    current_user: User = Depends(require_user),
):
    """Get all of user's favorite courts.
    Args:
        current_user: The authenticated user.
    Returns:
        list: User's favorite courts.
    """
    return FavoritesService.list_favorite_courts(current_user)


@router.post("/coaches/{coach_id}")
async def add_coach_favorite(
    coach_id: int,
    current_user: User = Depends(require_user),
    service: FavoritesService = Depends(get_favorites_service),
):
    """Add a coach to user's favorite coaches.
    Args:
        coach_id: The coach user ID to add.
        current_user: The authenticated user.
        service: FavoritesService instance.
    Returns:
        dict: Success message.
    """
    return await service.add_coach_to_favorites(current_user, coach_id)


@router.delete("/coaches/{coach_id}")
async def remove_coach_favorite(
    coach_id: int,
    current_user: User = Depends(require_user),
    service: FavoritesService = Depends(get_favorites_service),
):
    """Remove a coach from user's favorite coaches.
    Args:
        coach_id: The coach user ID to remove.
        current_user: The authenticated user.
        service: FavoritesService instance.
    Returns:
        dict: Success message.
    """
    return await service.remove_coach_from_favorites(current_user, coach_id)


@router.get("/coaches")
async def get_favorite_coaches(
    current_user: User = Depends(require_user),
):
    """Get all of user's favorite coaches.
    Args:
        current_user: The authenticated user.
    Returns:
        list: User's favorite coaches.
    """
    return FavoritesService.list_favorite_coaches(current_user)
