from enum import Enum
from decimal import Decimal
from sqlmodel import SQLModel, Field


class ServiceCategory(str, Enum):
    INDIVIDUAL = "individual"
    GROUP = "group"


class ServiceBase(SQLModel):
    __tablename__ = "services" # type: ignore
    name: str = Field(index=True)
    description: str | None = None
    price: Decimal = Field(gt=0)
    duration_minutes: int = Field(gt=0)
    is_available: bool = Field(default=True)
    category: ServiceCategory = Field(default=ServiceCategory.INDIVIDUAL)
    requires_coach: bool = False


class Service(ServiceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class ServiceCreate(ServiceBase):
    pass


class ServiceRead(ServiceBase):
    id: int
