"""Сервис для работы с пользователями"""
from uuid import uuid4
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.db.models import User
from app.schemas.users import UserCreate, UserResponse
from app.utils.logger import logger, log_id_filter


async def create_user_service(user_data: UserCreate, db: AsyncSession) -> UserResponse:
    """
    Создаёт нового пользователя.
    """
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        # Проверяем, не существует ли пользователь с таким telegram_id
        existing_user = await db.execute(select(User).filter_by(telegram_id=user_data.telegram_id))
        if existing_user.scalars().first():
            logger.error(f"Пользователь с telegram_id {user_data.telegram_id} уже существует")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким telegram_id уже существует"
            )
        # Создаём нового пользователя
        user = User(
            telegram_id=user_data.telegram_id,
            username=user_data.username
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Создан пользователь с id {user.id}, telegram_id {user.telegram_id}")
        return UserResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            created_at=user.created_at
        )
    except Exception as e:
        logger.error(f"Ошибка при создании пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при создании пользователя"
        )
    finally:
        log_id_filter.log_id = None


async def get_user_by_id_service(user_id: int, db: AsyncSession) -> Optional[UserResponse]:
    """
    Получает пользователя по его id.
    """
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        result = await db.execute(select(User).filter_by(id=user_id))
        user = result.scalars().first()
        if not user:
            logger.warning(f"Пользователь с id {user_id} не найден")
            return None

        logger.info(f"Получен пользователь с id {user_id}")
        return UserResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            created_at=user.created_at
        )
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя с id {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при получении пользователя"
        )
    finally:
        log_id_filter.log_id = None


async def get_user_by_telegram_id_service(telegram_id: str, db: AsyncSession) -> Optional[UserResponse]:
    """
    Получает пользователя по его telegram_id.
    """
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        result = await db.execute(select(User).filter_by(telegram_id=telegram_id))
        user = result.scalars().first()
        if not user:
            logger.warning(f"Пользователь с telegram_id {telegram_id} не найден")
            return None

        logger.info(f"Получен пользователь с telegram_id {telegram_id}")
        return UserResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            created_at=user.created_at
        )
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя с telegram_id {telegram_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при получении пользователя"
        )
    finally:
        log_id_filter.log_id = None


async def update_user_service(user_id: int, user_data: UserCreate, db: AsyncSession) -> UserResponse:
    """
    Обновляет данные пользователя.
    """
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        result = await db.execute(select(User).filter_by(id=user_id))
        user = result.scalars().first()
        if not user:
            logger.error(f"Пользователь с id {user_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        # Проверяем, не занят ли telegram_id другим пользователем
        if user_data.telegram_id != user.telegram_id:
            existing_user = await db.execute(select(User).filter_by(telegram_id=user_data.telegram_id))
            if existing_user.scalars().first():
                logger.error(f"Пользователь с telegram_id {user_data.telegram_id} уже существует")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким telegram_id уже существует"
                )
        user.telegram_id = user_data.telegram_id
        user.username = user_data.username
        await db.commit()
        await db.refresh(user)
        logger.info(f"Обновлён пользователь с id {user_id}")
        return UserResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            created_at=user.created_at
        )
    except Exception as e:
        logger.error(f"Ошибка при обновлении пользователя с id {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при обновлении пользователя"
        )
    finally:
        log_id_filter.log_id = None


async def delete_user_service(user_id: int, db: AsyncSession) -> None:
    """
    Удаляет пользователя по его id.
    """
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        result = await db.execute(select(User).filter_by(id=user_id))
        user = result.scalars().first()
        if not user:
            logger.error(f"Пользователь с id {user_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        await db.delete(user)
        await db.commit()
        logger.info(f"Удалён пользователь с id {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при удалении пользователя с id {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при удалении пользователя"
        )
    finally:
        log_id_filter.log_id = None


async def get_all_users_service(db: AsyncSession) -> List[UserResponse]:
    """
    Получает список всех пользователей.
    """
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        result = await db.execute(select(User).order_by(User.created_at))
        users = result.scalars().all()
        logger.info(f"Получено {len(users)} пользователей")
        return [
            UserResponse(
                id=user.id,
                telegram_id=user.telegram_id,
                username=user.username,
                created_at=user.created_at
            )
            for user in users
        ]
    except Exception as e:
        logger.error(f"Ошибка при получении списка пользователей: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при получении списка пользователей"
        )
    finally:
        log_id_filter.log_id = None
