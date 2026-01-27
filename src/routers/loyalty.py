"""Loyalty program API endpoints.
Handles loyalty account information and point adjustments.
"""

from fastapi import APIRouter, Depends
from ..models.loyalty import LoyaltyAccountRead, LoyaltyAdjust
from ..auth.dependencies import require_user, require_admin
from ..models.user import User
from ..core.dependencies_services import get_loyalty_service
from ..services.loyalty_service import LoyaltyService
from ..core.exceptions import ForbiddenActionError

router = APIRouter(prefix="/loyalty", tags=["Loyalty"])


@router.get("/", response_model=LoyaltyAccountRead)
async def show_loyalty_info(current_user: User = Depends(require_user)):
    """Get current user's loyalty account information.
    Args:
        current_user: The authenticated user.
    Returns:
        LoyaltyAccountRead: User's loyalty points and tier level.
    """
    return LoyaltyService.get_loyalty_info(current_user)


@router.post("/adjust", response_model=LoyaltyAccountRead)
async def adjust_loyalty_points(
    adjustment: LoyaltyAdjust,
    current_user: User = Depends(require_admin),
    service: LoyaltyService = Depends(get_loyalty_service),
):
    """Adjust a user's loyalty points (admin only).
    Args:
        adjustment: Adjustment data including user ID and points change.
        current_user: Must be an admin user.
        service: LoyaltyService instance.
    Returns:
        LoyaltyAccountRead: The updated loyalty account.
    """
    return await service.change_loyalty_points(current_user, adjustment.points_change)
