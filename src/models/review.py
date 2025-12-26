from enum import Enum
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .user import User
    from .court import Court


class ReviewTargetType(str, Enum):
    COURT = "court"
    SERVICE = "service"
    COACH = "coach"


class ReviewBase(SQLModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=500)
    target_type: ReviewTargetType = Field(index=True)
    target_id: int = Field(index=True)


class Review(ReviewBase, table=True):
    __tablename__ = "reviews"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.now)
    court_id: int | None = Field(default=None, foreign_key="courts.id")

    user: "User" = Relationship(back_populates="reviews")
    court: Optional["Court"] = Relationship(back_populates="reviews")


class ReviewCreate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    id: int
    created_at: datetime
    user_id: int
