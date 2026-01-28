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
    """Court surface material enumeration."""

    HARD = "hard"
    CLAY = "clay"
    GRASS = "grass"
    INDOOR = "indoor"


class CourtBase(SQLModel):
    """Base court data shared between models."""

    number: int = Field(unique=True, index=True)
    surface: Surface
    open_time: str | None = Field(default="08:00")
    close_time: str | None = Field(default="22:00")
    has_lighting: bool = Field(default=False)
    price_per_hour: Decimal = Field(default=25.0, ge=15.0)
    available: bool = Field(default=True)


class Court(CourtBase, table=True):
    """Court database model with relationships to reservations and reviews."""

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
    """Schema for creating a new court."""

    pass


class CourtRead(CourtBase):
    """Schema for reading court information."""

    pass
