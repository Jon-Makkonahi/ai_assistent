from uuid import uuid4

from celery import Celery
from sqlalchemy.future import select

from app.utils.logger import logger, log_id_filter
from app.db.models import Task, TaskStatus, Message, SenderType
from app.db.database import async_session_maker
from app.core.config import URL_REDIS


celery_app = Celery("ai_assistant", broker=URL_REDIS)


@celery_app.task
async def process_ai_task(task_id: str, input_data: str):
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    async with async_session_maker() as db:
        try:
            logger.info(f"Обработка задачи {task_id}")
            result = f"Processed: {input_data}"
            task_result = await db.execute(select(Task).filter_by(task_id=task_id))
            task = task_result.scalars().first()
            if task:
                task.status = TaskStatus.COMPLETED
                task.result = result
                await db.commit()
                logger.info(f"Задача {task_id} завершена")
                message = Message(
                    user_id=task.user_id,
                    task_id=task.id,
                    sender=SenderType.ASSISTANT,
                    content=result
                )
                db.add(message)
                await db.commit()
                logger.info(f"Создано сообщение от ассистента для задачи {task_id}")
            else:
                logger.error(f"Задача {task_id} не найдена в базе данных")
            return result
        except Exception as e:
            logger.error(f"Ошибка обработки задачи {task_id}: {e}")
            task_result = await db.execute(select(Task).filter_by(task_id=task_id))
            task = task_result.scalars().first()
            if task:
                task.status = TaskStatus.FAILED
                task.result = str(e)
                await db.commit()
                logger.info(f"Статус задачи {task_id} изменён на FAILED")
            raise
        finally:
            log_id_filter.log_id = None
