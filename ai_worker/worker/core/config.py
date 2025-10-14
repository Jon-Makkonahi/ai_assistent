"""Конфигурация воркера AI"""
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../../.env")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt2")  # Имя модели для transformers
