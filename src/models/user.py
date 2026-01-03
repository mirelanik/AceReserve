from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from .loyalty import LoyaltyAccount, LoyaltyLevel
    from .reservation import Reservation
    from .service import Service
    from .review import Review


class Role(str, Enum):
    GUEST = "guest"
    USER = "user"
    COACH = "coach"
    ADMIN = "admin"


class UserBase(SQLModel):
    full_name: str
    email: str = Field(index=True, unique=True)


class User(UserBase, table=True):
    __tablename__ = "users"  # type: ignore
    id: int = Field(default=None, primary_key=True)
    hashed_password: str

    role: Role = Field(default=Role.USER)

    loyalty: Optional["LoyaltyAccount"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"uselist": False}
    )
    reservations: list["Reservation"] = Relationship(back_populates="user")
    reviews: list["Review"] = Relationship(back_populates="user")
    services: list["Service"] = Relationship(back_populates="coach")

    @property
    def loyalty_points(self) -> int:
        if self.loyalty:
            return self.loyalty.points
        return 0

    @property
    def loyalty_level(self) -> Optional["LoyaltyLevel"]:
        if self.loyalty:
            return self.loyalty.level
        return None


class UserCreate(UserBase):
    email: str
    password: str
    full_name: str


class UserRead(UserBase):
    id: int
    role: Role
    loyalty_points: int
