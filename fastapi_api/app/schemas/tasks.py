from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from fastapi_api.app.db.models import TaskStatus


class TaskBase(BaseModel):
    input_data: str


class TaskCreate(TaskBase):
    user_id: int


class TaskResponse(TaskBase):
    id: int
    task_id: str
    status: TaskStatus
    result: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[str] = None
