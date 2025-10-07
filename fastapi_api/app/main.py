""" Корневой файл API """
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

# from app.api.chat import chat_router, tasks_router
from app.utils.loggers import setup_logging


# Создаём приложение FastAPI
app = FastAPI(
    title="FastAPI ИИ ассистента",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "null"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"]
)
setup_logging(app)

root_router = APIRouter(prefix="", tags=["root"])


# Корневой эндпоинт для проверки
@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API ИИ ассистента!"}


# вложение и подключение
# root_router.include_router(chat_router, prefix="/api")
# root_router.include_router(tasks_router, prefix="/api")
app.include_router(root_router)
