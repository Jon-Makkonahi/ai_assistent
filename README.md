# ai_assistent
ИИ ассистент для чата

Общая идея

Проект делится на три основных компонента:
1) FastAPI API – шлюз, который принимает запросы от клиентов (например, Telegram-бота) и ставит задачи в очередь.
2) AI Worker – микросервис, который выполняет обработку запросов с помощью ИИ (HuggingFace или локальная модель).
3) Telegram Bot (aiogram) – интерфейс для пользователя, который отправляет сообщения и получает ответы.

## Структура проекта
```
ai_assistant/
├── fastapi_api/       # FastAPI Gateway
│   ├── app/
│   │   ├── main.py           # Точка входа
│   │   ├── api/chat.py       # Эндпоинты: /chat, /status
│   │   ├── core/config.py    # Настройки приложения
│   │   ├── core/celery_app.py # Настройка очереди
│   │   ├── db/               # Подключение и модели базы данных
│   │   ├── services/tasks.py # Логика постановки задач
│   │   └── utils/logger.py   # Логирование
├── ai_worker/        # AI Worker
│   ├── worker/tasks/ai_tasks.py  # Функции генерации ответов через HuggingFace
│   ├── core/openai_client.py      # API-клиент HuggingFace / локальная модель
├── telegram_bot/     # Telegram бот
│   ├── bot/handlers/ chat.py      # Основная логика общения
│   ├── bot/services/api_client.py # Общение с FastAPI
│   └── bot/core/config.py         # Токен бота, адрес API
├── docker-compose.yml # Поднимает все сервисы
├── .env               # Переменные окружения
└── docs/              # Документация проекта
```

