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
    __tablename__ = "user_court_favorites"  # type: ignore
    user_id: int = Field(foreign_key="users.id", primary_key=True)
    court_id: int = Field(foreign_key="courts.id", primary_key=True)


class UserCoachFavorite(SQLModel, table=True):
    __tablename__ = "user_coach_favorites"  # type: ignore
    user_id: int = Field(foreign_key="users.id", primary_key=True)
    coach_id: int = Field(foreign_key="users.id", primary_key=True)


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
    reviews_written: list["Review"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "Review.author_id"},
    )
    services: list["Service"] = Relationship(back_populates="coach")

    favorite_courts: list["Court"] = Relationship(
        back_populates="favorited_by", link_model=UserCourtFavorite
    )

    favorite_coaches: list["User"] = Relationship(
        link_model=UserCoachFavorite,
        sa_relationship_kwargs={
            "primaryjoin": "User.id==user_coach_favorites.c.user_id",
            "secondaryjoin": "User.id==user_coach_favorites.c.coach_id",
        },
    )

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
