from fastapi import APIRouter, Depends
from ..models.loyalty import LoyaltyAccountRead, LoyaltyAdjust
from ..auth.dependencies import require_user
from ..models.user import User
from ..services.loyalty_service import get_loyalty_info, change_loyalty_points
from ..core.database import get_session
from ..models.user import Role
from ..core.exceptions import ForbiddenActionError

router = APIRouter(prefix="/loyalty", tags=["Loyalty"])


@router.get("/", response_model=LoyaltyAccountRead)
def show_loyalty_info(current_user: User = Depends(require_user)):
    return get_loyalty_info(current_user)


@router.post("/adjust", response_model=LoyaltyAccountRead)
def adjust_loyalty_points(
    adjustment: LoyaltyAdjust,
    current_user: User = Depends(require_user),
    session=Depends(get_session),
):
    if current_user.role != Role.ADMIN:
        raise ForbiddenActionError()

    return change_loyalty_points(session, current_user, adjustment.points_change)
