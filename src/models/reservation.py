from enum import Enum
from decimal import Decimal
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
from pydantic import field_validator

if TYPE_CHECKING:
    from .user import User
    from .court import Court


class ReservationStatus(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class ReservationBase(SQLModel):
    start_time: datetime
    duration_minutes: int = Field(default=60, ge=30)
    court_id: int = Field(foreign_key="courts.id")
    service_id: int | None = None
    rent_racket: bool = Field(default=False)
    rent_balls: bool = Field(default=False)
    notes: str | None = None


class Reservation(ReservationBase, table=True):
    __tablename__ = "reservations"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    status: ReservationStatus = Field(default=ReservationStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)
    end_time: datetime
    total_price: Decimal = Field(default=0.0)
    user_id: int = Field(foreign_key="users.id")

    user: "User" = Relationship(back_populates="reservations")
    court: "Court" = Relationship(back_populates="reservations")


class ReservationCreate(ReservationBase):
    @field_validator("duration_minutes")
    @classmethod
    def enforce_valid_duration(cls, value: int):
        if value % 30 != 0:
            raise ValueError(
                "Duration must be a multiple of 30 minutes (e.g. 30, 60, 90, etc.)"
            )
        return value


class ReservationRead(ReservationBase):
    id: int
    status: ReservationStatus
    created_at: datetime
    user_id: int
