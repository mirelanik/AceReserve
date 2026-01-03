from enum import Enum
from typing import TYPE_CHECKING
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User


class ServiceCategory(str, Enum):
    INDIVIDUAL = "individual"
    GROUP = "group"


class ServiceBase(SQLModel):
    name: str = Field(index=True)
    description: str | None = None
    price: Decimal = Field(gt=0)
    duration_minutes: int = Field(gt=0)
    is_available: bool = Field(default=True)
    category: ServiceCategory = Field(default=ServiceCategory.INDIVIDUAL)
    requires_coach: bool = False

class Service(ServiceBase, table=True):
    __tablename__ = "services"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)

    coach_id: int | None = Field(default=None, foreign_key="users.id")
    coach: "User" = Relationship(back_populates="services")

    @property
    def coach_name(self) -> str:
        return self.coach.full_name

class ServiceCreate(ServiceBase):
    pass


class ServiceRead(ServiceBase):
    id: int
    coach_name: str
