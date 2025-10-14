"""Задачи Celery для обработки AI-задач"""
import asyncio
import logging
from celery import Celery
from celery.utils.log import get_task_logger
from sqlalchemy.future import select
from uuid import uuid4

from ai_worker.worker.core.config import REDIS_URL
from ai_worker.worker.core.huggingai_client import HuggingFaceClient
from ai_worker.worker.utils.logger import logger, log_id_filter
from fastapi_api.app.db.database import async_session_maker
from fastapi_api.app.db.models import Task, TaskStatus, Message, SenderType


celery_logger = get_task_logger("ai_assistant")
celery_logger.handlers = logger.handlers
celery_logger.setLevel(logging.DEBUG)
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
    task_ignore_result=False,
    task_store_errors_even_if_ignored=True,
    worker_pool="solo",
    task_track_started=True,
)


async def _process_ai_task(task_id: str, input_data: str):
    logger.debug(f"Начало обработки задачи {task_id} с входными данными: {input_data}")
    client = None
    async with async_session_maker() as db:
        try:
            logger.debug("Инициализация HuggingFaceClient")
            client = HuggingFaceClient()
            logger.debug("Вызов generate_text")
            result = client.generate_text(input_data)
            logger.debug(f"Получен результат: {result}")

            logger.debug(f"Запрос задачи {task_id} из базы данных")
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
            raise
        finally:
            if client:
                client.cleanup()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_ai_task(self, task_id: str, input_data: str):
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        logger.debug(f"Запуск process_ai_task для task_id={task_id}")
        result = asyncio.run(_process_ai_task(task_id, input_data))
        logger.info(f"Успешно выполнен process_ai_task для task_id={task_id}")
        return result
    except Exception as e:
        logger.error(f"Ошибка в process_ai_task для task_id={task_id}: {str(e)}")
        raise
    finally:
        log_id_filter.log_id = None