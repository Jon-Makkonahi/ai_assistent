"""Сервис для обработки чатов и задач"""
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.db.models import Task, TaskStatus, Message, SenderType
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.helpers import service_wrapper
from app.worker.main import process_ai_task
from app.services.users import get_user_by_id_service


@service_wrapper
async def create_chat_service(request: ChatRequest,
                              db: AsyncSession) -> ChatResponse:
    """Создаёт задачу и сообщение от пользователя,
    отправляет задачу в Celery."""
    user = await get_user_by_id_service(request.user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Пользователь не найден")
    task_id = str(uuid4())
    task = Task(
        task_id=task_id,
        user_id=request.user_id,
        input_data=request.message,
        status=TaskStatus.PENDING
    )
    db.add(task)
    await db.flush()
    message = Message(
        user_id=request.user_id,
        task_id=task.id,
        sender=SenderType.USER,
        content=request.message
    )
    db.add(message)
    await db.commit()
    await db.refresh(task)
    process_ai_task.delay(task_id, request.message)
    return ChatResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        message="Задача успешно отправлена"
    )
