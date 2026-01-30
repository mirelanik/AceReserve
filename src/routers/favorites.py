from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user import User
from ..core.dependencies_services import get_favorites_service
from ..core.async_database import get_async_session
from ..services.favorites_services import FavoritesService
from ..auth.dependencies import require_user

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post("/courts/{court_number}", status_code=200)
async def add_court_favorite(
    court_number: int,
    current_user: User = Depends(require_user),
    service: FavoritesService = Depends(get_favorites_service),
):
    return await service.add_court_to_favorites(current_user, court_number)


@router.delete("/courts/{court_number}", status_code=200)
async def remove_court_favorite(
    court_number: int,
    current_user: User = Depends(require_user),
    service: FavoritesService = Depends(get_favorites_service),
):
    return await service.remove_court_from_favorites(current_user, court_number)


@router.get("/courts", status_code=200)
async def get_favorite_courts(
    current_user: User = Depends(require_user),
):
    return FavoritesService.list_favorite_courts(current_user)


@router.post("/coaches/{coach_id}", status_code=200)
async def add_coach_favorite(
    coach_id: int,
    current_user: User = Depends(require_user),
    service: FavoritesService = Depends(get_favorites_service),
):
    return await service.add_coach_to_favorites(current_user, coach_id)


@router.delete("/coaches/{coach_id}", status_code=200)
async def remove_coach_favorite(
    coach_id: int,
    current_user: User = Depends(require_user),
    service: FavoritesService = Depends(get_favorites_service),
):
    return await service.remove_coach_from_favorites(current_user, coach_id)


@router.get("/coaches", status_code=200)
async def get_favorite_coaches(
    current_user: User = Depends(require_user),
    session: AsyncSession = Depends(get_async_session),
):
    await session.refresh(current_user, ["favorite_coaches"])
    return FavoritesService.list_favorite_coaches(current_user)
