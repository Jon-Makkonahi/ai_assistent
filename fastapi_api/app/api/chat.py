"""API для обработки чатов и задач"""
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.utils.logger import logger, log_id_filter
from app.db.database import get_async_db
from app.db.models import Task, TaskStatus, Message, SenderType, User
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.tasks import TaskStatusResponse
from app.schemas.messages import MessageResponse

# Если используется Celery
# from app.worker.main import process_ai_task

chat_router = APIRouter(prefix="/api", tags=["chat"])
tasks_router = APIRouter(prefix="/api", tags=["tasks"])
messages_router = APIRouter(prefix="/api", tags=["messages"])


@chat_router.post("/chat", response_model=ChatResponse)
async def create_chat(request: ChatRequest,
                      db: AsyncSession = Depends(get_async_db)):
    """
    Создаёт задачу и сообщение от пользователя, отправляет задачу в обработку.
    """
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        # Проверяем, существует ли пользователь
        user_result = await db.execute(select(User).filter_by(id=request.user_id))
        user = user_result.scalars().first()
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
        await db.flush()  # Получаем task.id без коммита

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

        # Если используется Celery, отправляем задачу в очередь
        # process_ai_task.delay(task_id, request.message)

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

@tasks_router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, db: AsyncSession = Depends(get_async_db)):
    """
    Получает статус задачи по её task_id.
    """
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        result = await db.execute(select(Task).filter_by(task_id=task_id))
        task = result.scalars().first()
        if not task:
            logger.error(f"Задача с task_id {task_id} не найдена")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )

        logger.info(f"Получен статус задачи {task_id}: {task.status}")
        return TaskStatusResponse(
            task_id=task.task_id,
            status=task.status,
            result=task.result
        )
    except Exception as e:
        logger.error(f"Ошибка при получении статуса задачи {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при получении статуса задачи"
        )
    finally:
        log_id_filter.log_id = None


@chat_router.get("/messages/{user_id}", response_model=List[MessageResponse])
async def get_user_messages(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Получает историю сообщений пользователя.
    """
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        result = await db.execute(select(Message).filter_by(user_id=user_id).order_by(Message.created_at))
        messages = result.scalars().all()
        if not messages:
            logger.warning(f"Сообщения для пользователя {user_id} не найдены")
            return []

        logger.info(f"Получена история сообщений для пользователя {user_id}, найдено {len(messages)} сообщений")
        return [
            MessageResponse(
                id=message.id,
                sender=message.sender,
                content=message.content,
                created_at=message.created_at
            )
            for message in messages
        ]
    except Exception as e:
        logger.error(f"Ошибка при получении сообщений для пользователя {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при получении сообщений"
        )
    finally:
        log_id_filter.log_id = None
