"""Задачи Celery для обработки AI-задач"""
from celery import Celery
from sqlalchemy.future import select

from ai_worker.worker.core.config import REDIS_URL
from ai_worker.worker.core.huggingai_client import HuggingFaceClient
from ai_worker.worker.utils.logger import logger
from ai_worker.worker.utils.helpers import celery_service_wrapper
from fastapi_api.app.db.database import async_session_maker
from fastapi_api.app.db.models import Task, TaskStatus, Message, SenderType

celery_app = Celery(
    "ai_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
@celery_service_wrapper
async def process_ai_task(self, task_id: str, input_data: str):
    """Обрабатывает задачу через AI и обновляет её статус."""
    client = None
    async with async_session_maker() as db:
        try:
            client = HuggingFaceClient()
            result = await client.generate_text(input_data)

            task_result = await db.execute(select(Task).filter_by(task_id=task_id))
            task = task_result.scalars().first()
            if not task:
                logger.error(f"Задача {task_id} не найдена")
                raise ValueError(f"Задача {task_id} не найдена")

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
            logger.info(f"Задача {task_id} успешно обработана")
            return result
        except Exception as e:
            logger.error(f"Ошибка обработки задачи {task_id}: {str(e)}")
            task_result = await db.execute(select(Task).filter_by(task_id=task_id))
            task = task_result.scalars().first()
            if task:
                task.status = TaskStatus.FAILED
                task.result = str(e)
                await db.commit()
            self.retry(exc=e, countdown=60)
        finally:
            if client:
                client.cleanup()
