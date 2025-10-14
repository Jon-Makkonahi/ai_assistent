"""Сервис для управления задачами"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from fastapi_api.app.db.models import Task
from fastapi_api.app.schemas.tasks import TaskStatusResponse
from fastapi_api.app.utils.helpers import service_wrapper


@service_wrapper
async def get_task_status_service(task_id: str,
                                  db: AsyncSession) -> TaskStatusResponse:
    """Получает статус задачи по её task_id."""
    result = await db.execute(select(Task).filter_by(task_id=task_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Задача не найдена")
    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status,
        result=task.result
    )
