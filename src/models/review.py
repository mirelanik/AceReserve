"""Review model and related schemas.
Defines the Review entity for rating courts, services, and coaches.
"""

from enum import Enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from pydantic import model_validator
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User
    from .court import Court
    from .service import Service


class ReviewTargetType(str, Enum):
    """Type of entity being reviewed."""

    COURT = "court"
    SERVICE = "service"
    COACH = "coach"


class ReviewBase(SQLModel):
    """Base review data shared between models."""

    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=500)
    target_type: ReviewTargetType = Field(index=True)


class Review(ReviewBase, table=True):
    """Review database model with relationships to reviewed entities."""

    __tablename__ = "reviews"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="users.id")
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
    user: "User" = Relationship(
        back_populates="reviews_written",
        sa_relationship_kwargs={"foreign_keys": "Review.author_id", "lazy": "selectin"},
    )

    @property
    def user_name(self) -> str:
        """Get the name of the review author."""
        if self.user:
            return self.user.full_name
        return "Unknown"

    @model_validator(mode="after")
    def check_single_target(self):
        """Validate that review targets exactly one entity."""
        targets = [self.court_number, self.coach_id, self.service_id]
        filled_count = sum(1 for t in targets if t is not None)
        if filled_count != 1:
            raise ValueError(
                "Review must target exactly one entity (Court, Coach, or Service)."
            )
        return self


class ReviewCreate(ReviewBase):
    """Schema for creating a new review."""

    court_number: int | None = None
    coach_id: int | None = None
    service_id: int | None = None


class ReviewRead(ReviewBase):
    """Schema for reading review information."""

    id: int
    created_at: datetime
    user_name: str

    court_number: int | None
    coach_id: int | None
    service_id: int | None
