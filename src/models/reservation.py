"""Reservation model and related schemas.
Defines the Reservation entity with status tracking and pricing information.
"""

from enum import Enum
from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator


if TYPE_CHECKING:
    from .user import User
    from .court import Court
    from .service import Service


class ReservationStatus(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class ReservationBase(SQLModel):
    court_number: int = Field(foreign_key="courts.number")
    start_time: datetime
    duration_minutes: int = Field(default=60, ge=30)
    service_id: int | None = None
    rent_racket: bool = Field(default=False)
    rent_balls: bool = Field(default=False)
    wants_lighting: bool = Field(default=False)
    notes: str | None = None


class Reservation(ReservationBase, table=True):
    __tablename__ = "reservations"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    status: ReservationStatus = Field(default=ReservationStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)
    end_time: datetime
    total_price: Decimal = Field(default=0.0)
    user_id: int = Field(foreign_key="users.id")

    user: "User" = Relationship(
        back_populates="reservations", sa_relationship_kwargs={"lazy": "selectin"}
    )
    court: "Court" = Relationship(
        back_populates="reservations", sa_relationship_kwargs={"lazy": "selectin"}
    )

    @property
    def user_name(self) -> str:
        """Get the name of the user who made this reservation."""
        return self.user.full_name


class ReservationCreate(ReservationBase):

    @field_validator("duration_minutes")
    @classmethod
    def enforce_valid_duration(cls, value: int):
        """Validate that duration is a multiple of 30 minutes.
        Args:
            value: The duration in minutes.
        Returns:
            int: The validated duration.
        """
        if value % 30 != 0:
            raise ValueError(
                "Duration must be a multiple of 30 minutes (e.g. 30, 60, 90, etc.)"
            )
        return value


class ReservationRead(ReservationBase):
    id: int
    user_id: int
    status: ReservationStatus
    created_at: datetime
    user_name: str
    end_time: datetime
    total_price: Decimal


class ReservationUpdate(SQLModel):
    court_number: int | None = None
    start_time: datetime | None = None
    duration_minutes: int | None = None

    rent_racket: bool | None = None
    rent_balls: bool | None = None
    wants_lighting: bool | None = None
    notes: str | None = None
