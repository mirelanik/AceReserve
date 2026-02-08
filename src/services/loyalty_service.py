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
        self.session = session

    @staticmethod
    def update_loyalty_level(account: LoyaltyAccount, points_change: int) -> None:
        """Update loyalty account with point change and recalculate tier.
        Updates the account balance and automatically determines the tier level
        based on total points."""

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

    async def get_loyalty_info(self, user: User) -> LoyaltyAccount:
        """Retrieve the loyalty account information for a user, creating one if it doesn't exist."""
        result = await self.session.execute(
            select(LoyaltyAccount).where(LoyaltyAccount.user_id == user.id)
        )
        loyalty_account = result.scalars().first()

        if not loyalty_account:
            return LoyaltyAccount(
                user_id=user.id, points=0, level=LoyaltyLevel.BEGINNER
            )
        return loyalty_account

    async def change_loyalty_points(
        self, user_id: int, adjustment: int
    ) -> LoyaltyAccount:
        """Adjust a user's loyalty points (admin only)."""
        result = await self.session.execute(
            select(LoyaltyAccount).where(LoyaltyAccount.user_id == user_id)
        )
        loyalty_account = result.scalars().first()

        if not loyalty_account:
            raise LoyaltyAccountNotFoundError()

        self.update_loyalty_level(loyalty_account, adjustment)

        self.session.add(loyalty_account)
        await self.session.commit()
        await self.session.refresh(loyalty_account)

        return loyalty_account
