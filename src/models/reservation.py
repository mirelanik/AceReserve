from enum import Enum
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

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
    duration_minutes: int = Field(default=60)
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
    user_id: int = Field(foreign_key="users.id")

    user: User = Relationship(back_populates="reservations")
    court: "Court" = Relationship(back_populates="reservations")


class ReservationCreate(ReservationBase):
    pass


class ReservationRead(ReservationBase):
    id: int
    status: ReservationStatus
    created_at: datetime
    user_id: int
