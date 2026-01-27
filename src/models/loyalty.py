"""Loyalty account model and related schemas.
Defines the LoyaltyAccount entity with point tracking and tier levels.
"""

from enum import Enum
from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User


class LoyaltyLevel(str, Enum):
    """Loyalty tier level enumeration."""

    BEGINNER = "beginner"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class LoyaltyPointsType(str, Enum):
    """Type of loyalty point transaction."""

    EARNED = "earned"
    USED = "used"
    EXPIRED = "expired"


class LoyaltyAccountBase(SQLModel):
    """Base loyalty account data shared between models."""

    points: int = Field(default=0, ge=0)
    level: LoyaltyLevel = Field(default=LoyaltyLevel.BEGINNER)


class LoyaltyAccount(LoyaltyAccountBase, table=True):
    """Loyalty account database model."""

    __tablename__ = "loyalty_accounts"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    updated_at: datetime = Field(default_factory=datetime.now)

    user: "User" = Relationship(back_populates="loyalty", sa_relationship_kwargs={"lazy": "selectin"})

    @property
    def user_name(self) -> str | None:
        """Get the name of the user owning this loyalty account."""
        if self.user:
            return self.user.full_name
        return None


class LoyaltyAccountRead(LoyaltyAccountBase):
    """Schema for reading loyalty account information."""

    pass


class LoyaltyAdjust(SQLModel):
    """Schema for adjusting loyalty points (admin only)."""

    user_id: int
    points_change: int
    reason: str | None = None
