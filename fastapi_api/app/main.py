""" Корневой файл API """
import os
from uuid import uuid4
from typing import Dict, Union

from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import init_db, close_db, async_engine
# from app.api.chat import chat_router, tasks_router
from app.utils.logger import log_id_filter, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекст жизненного цикла приложения"""
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        logger.info("🔄 Приложение запускается: инициализация ресурсов...")
        await init_db(app)
        ml_model = {"name": "SentimentAnalysisModel", "version": "1.0"}
        logger.info(f"✅ Модель ML загружена: {ml_model}")
        app.state.model = ml_model
        yield
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске приложения: {e}")
        raise
    finally:
        logger.info("🛑 Приложение останавливается: очистка ресурсов...")
        await close_db(app)
        if hasattr(app.state, "model"):
            logger.info("🔻 Выгрузка модели ML")
            app.state.model = None
        logger.info("✅ Ресурсы успешно очищены.")
        log_id_filter.log_id = None

# Создаём приложение FastAPI
app = FastAPI(
    title="FastAPI ИИ ассистента",
    version="0.1.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "null"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"]
)
os.makedirs("logs", exist_ok=True)


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    """Функция логирования работы FastAPI"""
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        response = await call_next(request)
        if response.status_code in [401, 402, 403, 404]:
            logger.warning(f"Request to {request.url.path} failed")
        else:
            logger.info(f"Successfully accessed {request.url.path}")
        return response
    except Exception as ex:
        logger.error(f"Request to {request.url.path} failed: {ex}")
        return JSONResponse(content={"success": False}, status_code=500)
    finally:
        log_id_filter.log_id = None


root_router = APIRouter(prefix="", tags=["root"])


# Корневой эндпоинт для проверки
@app.get("/")
async def root(request: Request) -> Dict[str, Union[str, Dict[str, str], None]]:
    """
    Корневой маршрут, подтверждающий, что API работает.
    Проверяет состояние подключения к базе данных и наличие ML-модели.
    """
    log_id = str(uuid4())
    log_id_filter.log_id = log_id
    try:
        db_status = getattr(request.app.state, "db_status", "disconnected")
        model_info = getattr(request.app.state, "model", None)
        logger.info("Корневой эндпоинт вызван")
        return {
            "message": "Добро пожаловать в API ИИ ассистента!",
            "db_status": db_status,
            "model": model_info,
        }
    finally:
        log_id_filter.log_id = None


# вложение и подключение
# root_router.include_router(chat_router, prefix="/api")
# root_router.include_router(tasks_router, prefix="/api")
app.include_router(root_router)
