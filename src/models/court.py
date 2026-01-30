"""Court model and related schemas."""

from enum import Enum
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .user import UserCourtFavorite, User

if TYPE_CHECKING:
    from .reservation import Reservation
    from .review import Review


class Surface(str, Enum):
    HARD = "hard"
    CLAY = "clay"
    GRASS = "grass"
    INDOOR = "indoor"


class CourtBase(SQLModel):
    number: int = Field(unique=True, index=True)
    surface: Surface
    has_lighting: bool = Field(default=False)
    price_per_hour: Decimal = Field(default=25.0, ge=15.0)


class Court(CourtBase, table=True):
    __tablename__ = "courts"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)

    reservations: list["Reservation"] = Relationship(
        back_populates="court", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: list["Review"] = Relationship(
        back_populates="court", sa_relationship_kwargs={"lazy": "selectin"}
    )

    favorited_by: list["User"] = Relationship(
        back_populates="favorite_courts",
        link_model=UserCourtFavorite,
    )


class CourtCreate(CourtBase):
    pass


class CourtRead(CourtBase):
    pass
