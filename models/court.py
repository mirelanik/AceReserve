from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field


class Surface(str, Enum):
    hard = "hard"
    clay = "clay"
    grass = "grass"
    indoor = "indoor"


class Court(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: int
    surface: Surface
    open_time: Optional[str] = Field(default="08:00")
    close_time: Optional[str] = Field(default="22:00")
    capacity_tribune: Optional[int] = Field(default=0)
    lighting: bool = Field(default=False)
    price_per_hour: float = Field(default=25.0)
    available: bool = Field(default=True)

