"""API для обработки чатов и задач"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.services.chat import create_chat_service
from app.services.tasks import get_task_status_service
from app.services.messages import get_user_messages_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.tasks import TaskStatusResponse
from app.schemas.messages import MessageResponse


chat_router = APIRouter(prefix="/api", tags=["chat"])
tasks_router = APIRouter(prefix="/api", tags=["tasks"])
messages_router = APIRouter(prefix="/api", tags=["messages"])


@chat_router.post("/chat", response_model=ChatResponse)
async def create_chat(request: ChatRequest,
                      db: AsyncSession = Depends(get_async_db)):
    """Создаёт задачу и сообщение от пользователя, отправляет задачу в обработку."""
    return await create_chat_service(request, db)


@tasks_router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str,
                          db: AsyncSession = Depends(get_async_db)):
    """Получает статус задачи по её task_id."""
    return await get_task_status_service(task_id, db)


@messages_router.get("/messages/{user_id}",
                     response_model=List[MessageResponse])
async def get_user_messages(user_id: int,
                            db: AsyncSession = Depends(get_async_db)):
    """Получает историю сообщений пользователя."""
    return await get_user_messages_service(user_id, db)
