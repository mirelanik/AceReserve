from typing import Optional
from enum import Enum
from datetime import datetime
from sqlmodel import SQLModel, Field

class ReservationStatus(str, Enum):
    pending = "Pending"
    confirmed = "Confirmed"
    cancelled = "Cancelled"
    completed = "Completed"
    
class Reservation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    start: str
    duration_minutes: int = 60
    status: ReservationStatus = ReservationStatus.pending
    user_id: int
    court_id: int
    service_id: Optional[int] = None
    rent_racket: bool = Field(default=False)
    rent_balls: bool = Field(default=False)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class ReservationCreate(SQLModel):
    start: datetime
    duration_minutes: int = 60
    court_id: int
    service_id: int
    rent_racket: bool = False
    rent_balls: bool = False
    notes: Optional[str] = None

