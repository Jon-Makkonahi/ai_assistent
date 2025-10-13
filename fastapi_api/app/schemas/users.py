from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    telegram_id: str
    username: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
