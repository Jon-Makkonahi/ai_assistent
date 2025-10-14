from celery import Celery
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.utils.helpers import service_wrapper
from app.db.models import Task, TaskStatus, Message, SenderType
from app.db.database import async_session_maker
from app.core.config import URL_REDIS


celery_app = Celery("ai_assistant", broker=URL_REDIS)


@celery_app.task
@service_wrapper
async def process_ai_task(task_id: str, input_data: str):
    """Обрабатывает задачу и обновляет её статус."""
    async with async_session_maker() as db:
        result = f"Processed: {input_data}"  # Замените на вызов AI
        task_result = await db.execute(select(Task).filter_by(task_id=task_id))
        task = task_result.scalars().first()
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Задача не найдена")

        task.status = TaskStatus.COMPLETED
        task.result = result
        message = Message(
            user_id=task.user_id,
            task_id=task.id,
            sender=SenderType.ASSISTANT,
            content=result
        )
        db.add(message)
        await db.commit()
        return result