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
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("Log: [%(log_id)s:%(asctime)s - %(levelname)s - %(message)s]")

    os.makedirs("logs", exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/ai_worker.log",
        maxBytes=500 * 1024 * 1024,  # 500 MB
        backupCount=10,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    log_id_filter = LogIdFilter()
    logger.addFilter(log_id_filter)
    logger.addHandler(file_handler)

    return logger, log_id_filter

logger, log_id_filter = setup_logger()
