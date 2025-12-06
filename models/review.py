from typing import Optional
from enum import Enum
from datetime import datetime
from sqlmodel import SQLModel, Field

class ReviewTargetType(str, Enum):
    court = "court"
    service = "service"
    coach = "coach"
    
class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rating: int
    comment: Optional[str] = None
    user_id: int
    target_type: ReviewTargetType = ReviewTargetType.court  
    target_id: int
    created_at: datetime = Field(default_factory=datetime.now)

class ReviewCreate(SQLModel):
    rating: int
    comment: Optional[str] = None
    target_type: ReviewTargetType = ReviewTargetType.court  
    target_id: int