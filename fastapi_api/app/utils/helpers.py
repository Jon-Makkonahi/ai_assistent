"""Утилиты для упрощения сервисов"""
from functools import wraps
from uuid import uuid4

from fastapi import HTTPException, status

from app.utils.logger import logger, log_id_filter


def service_wrapper(func):
    """
    Декоратор для логирования и обработки ошибок в сервисах.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        log_id = str(uuid4())
        log_id_filter.log_id = log_id
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Успешно выполнен {func.__name__}")
            return result
        except HTTPException as e:
            logger.error(f"Ошибка в {func.__name__}: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Необработанная ошибка в {func.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка сервера"
            )
        finally:
            log_id_filter.log_id = None
    return wrapper
