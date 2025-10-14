from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from fastapi_api.app.db.models import SenderType


class MessageBase(BaseModel):
    sender: SenderType
    content: str


class MessageCreate(MessageBase):
    user_id: int
    task_id: Optional[int] = None


class MessageResponse(MessageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
