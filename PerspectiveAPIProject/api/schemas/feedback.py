from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class FeedbackItem(BaseModel):
    componentName: str
    activeExpression: str
    comment: Optional[str] = None
    dateTime: datetime = Field(default_factory=datetime.utcnow)


class FeedbackBase(BaseModel):
    user_gpn: str = Field(..., description="Unique Global Personnel Number")
    user_name: str
    user_email: EmailStr


class FeedbackCreate(FeedbackBase):
    user_feedbacks: List[FeedbackItem]


class FeedbackUpdate(BaseModel):
    user_feedbacks: Optional[List[FeedbackItem]] = None


class Feedback(FeedbackBase):
    id: int
    user_feedbacks: List[FeedbackItem]
    updated_time: datetime

    class Config:
        from_attributes = True
