"""Асинхронное подключение к PostgreSQL"""
from uuid import uuid4
from typing import AsyncGenerator

from fastapi import FastAPI
from loguru import logger
from sqlalchemy.ext.asyncio import (create_async_engine, async_sessionmaker,
                                    AsyncSession)

from fastapi_api.app.core.config import DATABASE_URL
from fastapi_api.app.utils.logger import log_id_filter, logger


async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет асинхронную сессию SQLAlchemy
    для работы с базой данных PostgreSQL.
    """
    async with async_session_maker() as session:
        yield session


async def init_db(app: FastAPI) -> None:
    """
    Инициализация подключения к базе данных при старте приложения.
    """
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        logger.info("Инициализация подключения к базе данных...")
        app.state.db_session_maker = async_session_maker
        async with async_engine.connect() as conn:
            app.state.db_status = "connected"
            logger.info("Соединение с базой данных успешно установлено")
    except Exception as e:
        app.state.db_status = f"error: {str(e)}"
        logger.error(f"Не удалось подключиться к базе данных: {e}")
        raise
    finally:
        log_id_filter.log_id = None


async def close_db(app: FastAPI) -> None:
    """
    Закрытие соединений с базой данных при завершении приложения.
    """
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        logger.info("Закрытие соединений с базой данных...")
        if hasattr(app.state, "db_session_maker"):
            await async_engine.dispose()
            app.state.db_session_maker = None
            app.state.db_status = "disconnected"
            logger.info("Соединения с базой данных успешно закрыты")
    finally:
        log_id_filter.log_id = None
