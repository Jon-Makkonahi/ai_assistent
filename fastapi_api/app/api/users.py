"""API для работы с пользователями"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.services.users import (create_user_service, get_user_by_id_service,
                                get_user_by_telegram_id_service, update_user_service,
                                delete_user_service, get_all_users_service)
from app.schemas.users import UserCreate, UserResponse


users_router = APIRouter(prefix="/api/users", tags=["users"])


@users_router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate,
                      db: AsyncSession = Depends(get_async_db)):
    """Создаёт нового пользователя."""
    return await create_user_service(user_data, db)


@users_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """Получает пользователя по его id."""
    return await get_user_by_id_service(user_id, db)


@users_router.get("/telegram/{telegram_id}", response_model=UserResponse)
async def get_user_by_telegram_id(telegram_id: str,
                                  db: AsyncSession = Depends(get_async_db)):
    """Получает пользователя по его telegram_id."""
    return await get_user_by_telegram_id_service(telegram_id, db)


@users_router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserCreate,
                      db: AsyncSession = Depends(get_async_db)):
    """Обновляет данные пользователя."""
    return await update_user_service(user_id, user_data, db)


@users_router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """Удаляет пользователя."""
    await delete_user_service(user_id, db)
    return {"message": "Пользователь успешно удалён"}


@users_router.get("/", response_model=List[UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_async_db)):
    """Получает список всех пользователей."""
    return await get_all_users_service(db)
