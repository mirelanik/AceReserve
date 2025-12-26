from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .loyalty import LoyaltyAccount
    from .reservation import Reservation
    from .review import Review


class Role(str, Enum):
    GUEST = "guest"
    USER = "user"
    COACH = "coach"
    ADMIN = "admin"


class UserBase(SQLModel):
    full_name: str
    email: str = Field(index=True, unique=True)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    __tablename__ = "users"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str

    role: Role = Field(default=Role.USER)

    loyalty: "LoyaltyAccount | None" = Relationship(
        back_populates="user", sa_relationship_kwargs={"uselist": False}
    )
    reservations: list["Reservation"] = Relationship(back_populates="user")
    reviews: list["Review"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    email: str
    password: str
    full_name: str


class UserRead(UserBase):
    id: int
    role: Role
    loyalty_points: int
