"""Сервис для работы с сообщениями"""
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Message
from app.schemas.messages import MessageResponse
from app.utils.helpers import service_wrapper


@service_wrapper
async def get_user_messages_service(user_id: int,
                                    db: AsyncSession) -> List[MessageResponse]:
    """Получает историю сообщений пользователя."""
    result = await db.execute(
        select(Message).filter_by(user_id=user_id).order_by(Message.created_at)
    )
    messages = result.scalars().all()
    return [
        MessageResponse(
            id=message.id,
            sender=message.sender,
            content=message.content,
            created_at=message.created_at
        )
        for message in messages
    ]
