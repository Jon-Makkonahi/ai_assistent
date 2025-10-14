"""Сервис для работы с пользователями"""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from fastapi_api.app.db.models import User
from fastapi_api.app.schemas.users import UserCreate, UserResponse
from fastapi_api.app.utils.helpers import service_wrapper


@service_wrapper
async def create_user_service(user_data: UserCreate,
                              db: AsyncSession) -> UserResponse:
    """Создаёт нового пользователя."""
    existing_user = await db.execute(
        select(User).filter_by(telegram_id=user_data.telegram_id))
    if existing_user.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким telegram_id уже существует"
        )
    user = User(telegram_id=user_data.telegram_id, username=user_data.username)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        created_at=user.created_at
    )


@service_wrapper
async def get_user_by_id_service(user_id: int,
                                 db: AsyncSession) -> Optional[UserResponse]:
    """Получает пользователя по его id."""
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Пользователь не найден")
    return UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        created_at=user.created_at
    )


@service_wrapper
async def get_user_by_telegram_id_service(telegram_id: str,
                                          db: AsyncSession) -> Optional[UserResponse]:
    """Получает пользователя по его telegram_id."""
    result = await db.execute(select(User).filter_by(telegram_id=telegram_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Пользователь не найден")
    return UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        created_at=user.created_at
    )


@service_wrapper
async def update_user_service(user_id: int, user_data: UserCreate,
                              db: AsyncSession) -> UserResponse:
    """Обновляет данные пользователя."""
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Пользователь не найден")
    if user_data.telegram_id != user.telegram_id:
        existing_user = await db.execute(select(User).filter_by(
            telegram_id=user_data.telegram_id))
        if existing_user.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким telegram_id уже существует"
            )
    user.telegram_id = user_data.telegram_id
    user.username = user_data.username
    await db.commit()
    await db.refresh(user)
    return UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        created_at=user.created_at
    )


@service_wrapper
async def delete_user_service(user_id: int, db: AsyncSession) -> None:
    """Удаляет пользователя по его id."""
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Пользователь не найден")
    await db.delete(user)
    await db.commit()


@service_wrapper
async def get_all_users_service(db: AsyncSession) -> List[UserResponse]:
    """Получает список всех пользователей."""
    result = await db.execute(select(User).order_by(User.created_at))
    users = result.scalars().all()
    return [
        UserResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            created_at=user.created_at
        )
        for user in users
    ]
