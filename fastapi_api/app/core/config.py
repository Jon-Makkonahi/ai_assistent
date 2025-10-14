"""Конфигурация приложения FastAPI"""
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../../.env")  # Указываем путь к .env в корне проекта
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user_project:admin123@localhost:5432/project_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
