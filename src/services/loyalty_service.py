"""Loyalty program service.
Handles loyalty point management and tier level calculations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from ..models.user import User
from ..models.loyalty import LoyaltyAccount, LoyaltyLevel
from ..core.exceptions import LoyaltyAccountNotFoundError


class LoyaltyService:
    """Service for managing user loyalty accounts and points.

    Handles point updates, tier level calculations, and loyalty account operations.
    """

    def __init__(self, session: AsyncSession):
        """Initialize LoyaltyService with database session.

        Args:
            session: Async SQLAlchemy database session.
        """
        self.session = session

    @staticmethod
    def _update_loyalty_level(account: LoyaltyAccount, points_change: int) -> None:
        """Update loyalty account with point change and recalculate tier.

        Updates the account balance and automatically determines the tier level
        based on total points.

        Args:
            account: The loyalty account to update.
            points_change: Points to add (positive) or subtract (negative).
        """
        account.points += points_change
        account.points = max(account.points, 0)

        if account.points >= 300:
            account.level = LoyaltyLevel.PLATINUM
        elif account.points >= 150:
            account.level = LoyaltyLevel.GOLD
        elif account.points >= 50:
            account.level = LoyaltyLevel.SILVER
        else:
            account.level = LoyaltyLevel.BEGINNER

    @staticmethod
    def get_loyalty_info(user: User) -> dict:
        """Get loyalty information for a user.

        Args:
            user: The user to get loyalty info for.

        Returns:
            dict: Contains 'points' and 'level' keys.
        """
        if not user.loyalty:
            return {"points": 0, "level": LoyaltyLevel.BEGINNER}
        return {"points": user.loyalty.points, "level": user.loyalty.level}

    async def change_loyalty_points(
        self, user: User, adjustment: int
    ) -> LoyaltyAccount:
        """Adjust a user's loyalty points (admin only).

        Args:
            user: The user whose loyalty to adjust.
            adjustment: Points to add (positive) or subtract (negative).

        Returns:
            LoyaltyAccount: The updated loyalty account.

        Raises:
            LoyaltyAccountNotFoundError: If user has no loyalty account.
        """
        result = await self.session.execute(
            select(LoyaltyAccount).where(LoyaltyAccount.user_id == user.id)
        )
        loyalty_account = result.scalars().first()

        if not loyalty_account:
            raise LoyaltyAccountNotFoundError()

        self._update_loyalty_level(loyalty_account, adjustment)

        self.session.add(loyalty_account)
        await self.session.commit()
        await self.session.refresh(loyalty_account)

        return loyalty_account


# Module-level functions for backward compatibility
def update_loyalty_level(account: LoyaltyAccount, points_change: int) -> None:
    """Update loyalty account with point change and recalculate tier (module-level function).

    Args:
        account: The loyalty account to update.
        points_change: Points to add (positive) or subtract (negative).
    """
    LoyaltyService._update_loyalty_level(account, points_change)


def get_loyalty_info(user: User) -> dict:
    """Get loyalty information for a user (module-level function).

    Args:
        user: The user to get loyalty info for.

    Returns:
        dict: Contains 'points' and 'level' keys.
    """
    return LoyaltyService.get_loyalty_info(user)
