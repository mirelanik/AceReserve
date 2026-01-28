"""Service model and related schemas.
Defines the Service entity for coach-provided training services.
"""

from enum import Enum
from typing import TYPE_CHECKING
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User
    from .review import Review


class ServiceCategory(str, Enum):
    """Service category enumeration."""

    INDIVIDUAL = "individual"
    GROUP = "group"


class ServiceBase(SQLModel):
    """Base service data shared between models."""

    name: str = Field(index=True)
    description: str | None = None
    price: Decimal = Field(gt=0)
    duration_minutes: int = Field(gt=0)
    is_available: bool = Field(default=True)
    category: ServiceCategory = Field(default=ServiceCategory.INDIVIDUAL)
    requires_coach: bool = False


class Service(ServiceBase, table=True):
    """Service database model with relationships to coaches and reviews."""

    __tablename__ = "services"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)

    coach_id: int | None = Field(default=None, foreign_key="users.id")
    coach: "User" = Relationship(
        back_populates="services", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: list["Review"] = Relationship(
        back_populates="service", sa_relationship_kwargs={"lazy": "selectin"}
    )

    @property
    def coach_name(self) -> str:
        """Get the name of the coach providing this service."""
        return self.coach.full_name


class ServiceCreate(ServiceBase):
    """Schema for creating a new service."""

    coach_id: int | None = None


class ServiceRead(ServiceBase):
    """Schema for reading service information."""

    id: int
    coach_name: str
