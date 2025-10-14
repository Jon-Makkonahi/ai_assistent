"""Celery клиент для отправки задач в ai_worker"""
from celery import Celery

from fastapi_api.app.core.config import REDIS_URL


celery_app = Celery(
    "fastapi_ai_assistant",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)