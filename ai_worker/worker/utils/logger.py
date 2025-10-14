import logging
import logging.handlers
import os
from typing import Optional

class LogIdFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.log_id: Optional[str] = None

    def filter(self, record):
        record.log_id = self.log_id or "no-id"
        return True

def setup_logger():
    logger = logging.getLogger("ai_assistant")
    if logger.hasHandlers():
        logger.handlers.clear()  # Очищаем существующие обработчики, чтобы избежать дублирования
    logger.setLevel(logging.DEBUG)  # Устанавливаем DEBUG для большей детализации

    # Создаём директорию logs с проверкой ошибок
    try:
        os.makedirs("logs", exist_ok=True)
    except Exception as e:
        print(f"Ошибка создания директории logs: {str(e)}")
        raise

    # Настраиваем файловый обработчик
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            "logs/ai_worker.log",
            maxBytes=500 * 1024 * 1024,  # 500 MB
            backupCount=10,
            encoding="utf-8"
        )
        formatter = logging.Formatter("[%(log_id)s:%(asctime)s - %(levelname)s - %(message)s]")
        file_handler.setFormatter(formatter)
    except Exception as e:
        print(f"Ошибка настройки файлового обработчика: {str(e)}")
        raise

    # Добавляем консольный обработчик для отладки
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    # Настраиваем фильтр
    log_id_filter = LogIdFilter()
    logger.addFilter(log_id_filter)

    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Тестовый лог
    logger.debug("Логгер инициализирован")
    return logger, log_id_filter

try:
    logger, log_id_filter = setup_logger()
except Exception as e:
    print(f"Ошибка инициализации логгера: {str(e)}")
    raise
