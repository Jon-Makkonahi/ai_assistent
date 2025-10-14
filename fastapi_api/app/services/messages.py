"""Сервис для работы с сообщениями"""
from typing import List
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.db.models import Message
from app.schemas.messages import MessageResponse
from app.utils.logger import logger, log_id_filter


async def get_user_messages_service(user_id: int, db: AsyncSession) -> List[MessageResponse]:
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
