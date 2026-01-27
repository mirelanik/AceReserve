"""User model and related schemas.
Defines the User entity, Role enum, and related schemas for
user management and authentication.
"""

from enum import Enum
from typing import TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from .loyalty import LoyaltyAccount, LoyaltyLevel
    from .reservation import Reservation
    from .service import Service
    from .review import Review
    from .court import Court


class UserCourtFavorite(SQLModel, table=True):
    """Join table for user favorite courts relationship."""

    __tablename__ = "user_court_favorites"  # type: ignore
    user_id: int = Field(foreign_key="users.id", primary_key=True)
    court_id: int = Field(foreign_key="courts.id", primary_key=True)


class UserCoachFavorite(SQLModel, table=True):
    """Join table for user favorite coaches relationship."""

    __tablename__ = "user_coach_favorites"  # type: ignore
    user_id: int = Field(foreign_key="users.id", primary_key=True)
    coach_id: int = Field(foreign_key="users.id", primary_key=True)


class Role(str, Enum):
    """User role enumeration for role-based access control."""

    GUEST = "guest"
    USER = "user"
    COACH = "coach"
    ADMIN = "admin"


class UserBase(SQLModel):
    """Base user data shared between models."""

    full_name: str
    email: str = Field(index=True, unique=True)


class User(UserBase, table=True):
    """User database model with relationships to loyalty, reservations, and reviews."""

    __tablename__ = "users"  # type: ignore
    id: int = Field(default=None, primary_key=True)
    hashed_password: str

    role: Role = Field(default=Role.USER)

    loyalty: Optional["LoyaltyAccount"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False, "lazy": "selectin"},
    )
    reservations: list["Reservation"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews_written: list["Review"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "Review.author_id", "lazy": "selectin"},
    )
    services: list["Service"] = Relationship(
        back_populates="coach", sa_relationship_kwargs={"lazy": "selectin"}
    )

    favorite_courts: list["Court"] = Relationship(
        back_populates="favorited_by",
        link_model=UserCourtFavorite,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    favorite_coaches: list["User"] = Relationship(
        link_model=UserCoachFavorite,
        sa_relationship_kwargs={
            "primaryjoin": "User.id==user_coach_favorites.c.user_id",
            "secondaryjoin": "User.id==user_coach_favorites.c.coach_id",
            "lazy": "selectin",
        },
    )

    @property
    def loyalty_points(self) -> int:
        """Get user's current loyalty points."""
        return self.loyalty.points if self.loyalty else 0

    @property
    def loyalty_level(self) -> Optional["LoyaltyLevel"]:
        """Get user's loyalty level."""
        return self.loyalty.level if self.loyalty else None


class UserCreate(UserBase):
    """Schema for user registration and creation."""

    email: str
    password: str
    full_name: str


class UserRead(UserBase):
    """Schema for reading user information."""

    id: int
    role: Role
    loyalty_points: int
