"""Сервис для обработки чатов и задач"""
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.db.models import Task, TaskStatus, Message, SenderType, User
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.logger import logger, log_id_filter
from app.worker.main import process_ai_task
from app.services.users import get_user_by_id_service


async def create_chat_service(request: ChatRequest, db: AsyncSession) -> ChatResponse:
    """
    Создаёт задачу и сообщение от пользователя, отправляет задачу в Celery.
    """
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        # Проверяем, существует ли пользователь
        user = await get_user_by_id_service(request.user_id, db)
        if not user:
            logger.error(f"Пользователь с id {request.user_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        # Создаём задачу
        task_id = str(uuid4())
        task = Task(
            task_id=task_id,
            user_id=request.user_id,
            input_data=request.message,
            status=TaskStatus.PENDING
        )
        db.add(task)
        await db.flush()
        # Создаём сообщение
        message = Message(
            user_id=request.user_id,
            task_id=task.id,
            sender=SenderType.USER,
            content=request.message
        )
        db.add(message)
        await db.commit()
        await db.refresh(task)
        # Логируем создание задачи и сообщения
        logger.info(f"Создана задача {task_id} для пользователя {request.user_id}")
        logger.info(f"Создано сообщение от пользователя {request.user_id}")
        # Отправляем задачу в Celery
        process_ai_task.delay(task_id, request.message)
        return ChatResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="Задача успешно отправлена"
        )
    except Exception as e:
        logger.error(f"Ошибка при создании задачи/сообщения: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при обработке запроса"
        )
    finally:
        log_id_filter.log_id = None
