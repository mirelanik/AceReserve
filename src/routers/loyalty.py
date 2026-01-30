"""Loyalty program API endpoints.
Handles loyalty account information and point adjustments.
"""

from fastapi import APIRouter, Depends
from ..models.loyalty import LoyaltyAccountRead, LoyaltyAdjust
from ..auth.dependencies import require_user, require_admin
from ..models.user import User
from ..core.dependencies_services import get_loyalty_service
from ..services.loyalty_service import LoyaltyService

router = APIRouter(prefix="/loyalty", tags=["Loyalty"])


@router.get("/", response_model=LoyaltyAccountRead, status_code=200)
async def show_loyalty_info(current_user: User = Depends(require_user)):
    return LoyaltyService.get_loyalty_info(current_user)


@router.post("/adjust", response_model=LoyaltyAccountRead, status_code=200)
async def adjust_loyalty_points(
    adjustment: LoyaltyAdjust,
    current_user: User = Depends(require_admin),
    service: LoyaltyService = Depends(get_loyalty_service),
):
    return await service.change_loyalty_points(current_user, adjustment.points_change)
