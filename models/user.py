from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field


class Role(str, Enum):
    guest = "guest"
    user = "user"
    coach = "coach"
    admin = "admin"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    role: Role = Role.user


class UserCreate(SQLModel):
    name: str
    email: str
    role: Role = Role.user