from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field

class ServiceCategory(str, Enum):
    individual = "individual"
    group = "group"
    
class Service(SQLModel, table=True):
    id: Optional[int]
    category: ServiceCategory = ServiceCategory.individual
    coach: bool = False
    