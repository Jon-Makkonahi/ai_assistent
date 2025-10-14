"""Сервис для управления задачами"""
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.db.models import Task
from app.schemas.tasks import TaskStatusResponse
from app.utils.logger import logger, log_id_filter


async def get_task_status_service(task_id: str, db: AsyncSession) -> TaskStatusResponse:
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
