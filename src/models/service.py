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
    INDIVIDUAL = "individual"
    GROUP = "group"


class ServiceBase(SQLModel):
    name: str = Field(index=True)
    court_number: int = Field(foreign_key="courts.number")
    price: Decimal = Field(gt=0)
    duration_minutes: int = Field(gt=0)
    is_available: bool = Field(default=True)
    category: ServiceCategory = Field(default=ServiceCategory.INDIVIDUAL)
    requires_coach: bool = False
    max_group_capacity: int = Field(default=1, ge=1)


class Service(ServiceBase, table=True):
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
        return self.coach.full_name


class ServiceCreate(ServiceBase):
    coach_id: int | None = None


class ServiceRead(ServiceBase):
    id: int
    coach_name: str
