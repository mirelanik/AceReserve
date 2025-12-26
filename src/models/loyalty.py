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
    logs: list["LoyaltyLog"] = Relationship(back_populates="account")


class LoyaltyAccountRead(LoyaltyAccountBase):
    id: int
    user_id: int
    updated_at: datetime


class LoyaltyLogBase(SQLModel):
    amount: int
    points_type: LoyaltyPointsType
    description: str | None = None


class LoyaltyLog(LoyaltyLogBase, table=True):
    __tablename__ = "loyalty_logs"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="loyalty_accounts.id")
    created_at: datetime = Field(default_factory=datetime.now)

    account: "LoyaltyAccount" = Relationship(back_populates="logs")


class LoyaltyLogCreate(LoyaltyLogBase):
    pass


class LoyaltyLogRead(LoyaltyLogBase):
    id: int
    created_at: datetime
