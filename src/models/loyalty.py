from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class LoyaltyLevel(str, Enum):
    BEGINNER = "beginner"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class LoyaltyPointsType(str, Enum):
    EARNED = "earned"
    USED = "used"
    EXPIRED = "expired"


class LoyaltyAccountBase(SQLModel):
    points: int = Field(default=0, ge=0)
    level: LoyaltyLevel = Field(default=LoyaltyLevel.BEGINNER)


class LoyaltyAccount(LoyaltyAccountBase, table=True):
    __tablename__ = "loyalty_accounts"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    updated_at: datetime = Field(default_factory=datetime.now)

    user: "User" = Relationship(back_populates="loyalty")

    @property
    def user_name(self) -> str | None:
        if self.user:
            return self.user.full_name
        return None


class LoyaltyAccountRead(LoyaltyAccountBase):
    pass


class LoyaltyAdjust(SQLModel):
    user_id: int
    points_change: int
    reason: str | None = None
