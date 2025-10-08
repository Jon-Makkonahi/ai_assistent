"""Настройка логирования"""
import logging
import logging.handlers
import os
from typing import Optional
from queue import Empty
from multiprocessing import Queue
from threading import Thread


class LogIdFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.log_id: Optional[str] = None

    def filter(self, record: logging.LogRecord) -> bool:  # Исправляем тип record
        record.log_id = self.log_id or "no-id"
        return True

def setup_logger():
    logger = logging.getLogger("ai_assistant")
    logger.setLevel(logging.INFO)
    # Создаём очередь для логов
    log_queue = Queue()
    # Форматтер
    formatter = logging.Formatter("Log: [%(log_id)s:%(asctime)s - %(levelname)s - %(message)s]")
    # QueueHandler для отправки логов в очередь
    queue_handler = logging.handlers.QueueHandler(log_queue)
    # Фильтр для log_id
    log_id_filter = LogIdFilter()
    queue_handler.addFilter(log_id_filter)
    # Добавляем QueueHandler к логгеру
    logger.addHandler(queue_handler)
    # Создаём обработчики для консоли и файла
    os.makedirs("logs", exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/info.log",
        maxBytes=500 * 1024 * 1024,  # 500 MB
        backupCount=10,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    # Функция для обработки логов из очереди
    def log_worker():
        while True:
            try:
                record = log_queue.get()
                if record is None:  # Сигнал для завершения
                    break
                for handler in [file_handler, console_handler]:
                    handler.handle(record)
            except Empty:
                continue
            except Exception as e:
                print(f"Ошибка в log_worker: {e}")

    # Запускаем отдельный поток для обработки логов
    log_thread = Thread(target=log_worker, daemon=True)
    log_thread.start()
    
    return logger, log_id_filter

# Инициализация логгера только один раз
logger, log_id_filter = setup_logger()
