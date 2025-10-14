# fastapi_api/app/core/config.py
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../../.env")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user_project:admin123@localhost:5432/project_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://:admin123@localhost:6379/0")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt2")
PROJECT_NAME = os.getenv("PROJECT_NAME", "AI Assistant")
API_V1_STR = os.getenv("API_V1_STR", "/api")
