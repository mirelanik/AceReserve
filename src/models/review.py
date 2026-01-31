"""Review model and related schemas.
Defines the Review entity for rating courts, services, and coaches.
"""

from enum import Enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, ForeignKey
from pydantic import model_validator
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User
    from .court import Court
    from .service import Service


class ReviewTargetType(str, Enum):
    COURT = "court"
    SERVICE = "service"
    COACH = "coach"


class ReviewBase(SQLModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=500)
    target_type: ReviewTargetType = Field(index=True)


class Review(ReviewBase, table=True):
    __tablename__ = "reviews"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    author_id: int | None = Field(
        default=None,
        sa_column=Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    created_at: datetime = Field(default_factory=datetime.now)

    court_number: int | None = Field(default=None, foreign_key="courts.number")
    service_id: int | None = Field(default=None, foreign_key="services.id")
    coach_id: int | None = Field(default=None, foreign_key="users.id")

    court: Optional["Court"] = Relationship(
        back_populates="reviews", sa_relationship_kwargs={"lazy": "selectin"}
    )
    service: Optional["Service"] = Relationship(
        back_populates="reviews", sa_relationship_kwargs={"lazy": "selectin"}
    )
    user: Optional["User"] = Relationship(
        back_populates="reviews_written",
        sa_relationship_kwargs={"foreign_keys": "Review.author_id", "lazy": "selectin"},
    )

    @property
    def user_name(self) -> str:
        if self.user:
            return self.user.full_name
        return "Unknown"

    @model_validator(mode="after")
    def check_single_target(self):
        targets = [self.court_number, self.coach_id, self.service_id]
        filled_count = sum(1 for t in targets if t is not None)
        if filled_count != 1:
            raise ValueError(
                "Review must target exactly one entity (Court, Coach, or Service)."
            )
        return self


class ReviewCreate(ReviewBase):
    court_number: int | None = None
    coach_id: int | None = None
    service_id: int | None = None


class ReviewRead(ReviewBase):
    id: int
    created_at: datetime
    user_name: str

    court_number: int | None
    coach_id: int | None
    service_id: int | None
