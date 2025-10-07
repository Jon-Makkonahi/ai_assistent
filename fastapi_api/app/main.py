""" Корневой файл API """
from fastapi import FastAPI, APIRouter

from api.chat import chat_router, tasks_router


# Создаём приложение FastAPI
app = FastAPI(
    title="FastAPI ИИ ассистента",
    version="0.1.0",
)
root_router = APIRouter(prefix="", tags=["root"])


# Корневой эндпоинт для проверки
@root_router.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API ИИ ассистента!"}


# вложение и подключение
root_router.include_router(chat_router)
root_router.include_router(tasks_router)
app.include_router(root_router, prefix="/api")
