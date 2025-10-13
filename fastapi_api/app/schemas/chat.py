from pydantic import BaseModel
from app.db.models import TaskStatus


class ChatRequest(BaseModel):
    user_id: int
    message: str


class ChatResponse(BaseModel):
    task_id: str
    status: TaskStatus
    message: str
