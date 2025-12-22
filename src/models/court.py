from enum import Enum
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .reservation import Reservation
    from .review import Review


class Surface(str, Enum):
    HARD = "hard"
    CLAY = "clay"
    GRASS = "grass"
    INDOOR = "indoor"


class CourtBase(SQLModel):
    number: int = Field(unique=True)
    surface: Surface
    open_time: str | None = Field(default="08:00")
    close_time: str | None = Field(default="22:00")
    lighting: bool = Field(default=False)
    price_per_hour: Decimal = Field(default=25.0)
    available: bool = Field(default=True)


class Court(CourtBase, table=True):
    __tablename__ = "courts"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)

    reservations: list["Reservation"] = Relationship(back_populates="courts")
    reviews: list["Review"] = Relationship(back_populates="courts")
