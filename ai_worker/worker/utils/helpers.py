from functools import wraps
from uuid import uuid4

from ai_worker.utils.logger import logger, log_id_filter


def celery_service_wrapper(func):
    """
    Декоратор для логирования и обработки ошибок в Celery задачах.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        log_id = str(uuid4())
        log_id_filter.log_id = log_id
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Успешно выполнен {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Ошибка в {func.__name__}: {str(e)}")
            raise  # Передаем исключение Celery для обработки ретраев
        finally:
            log_id_filter.log_id = None
    return wrapper
