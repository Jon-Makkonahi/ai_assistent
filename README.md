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
├── fastapi_api/              # 🧠 FastAPI Gateway
│   ├── app/
│   │   ├── main.py           # Точка входа FastAPI
│   │   ├── api/              # Роутеры (эндпоинты)
│   │   │   ├── __init__.py
│   │   │   └── chat.py       # Эндпоинты: POST /api/chat, GET /api/status/{task_id}
│   │   ├── core/
│   │   │   ├── config.py     # Настройки окружения (env, брокер, API-ключи)
│   │   │   └── celery_app.py # Инициализация Celery (или RQ)
│   │   ├── db/
│   │   │   ├── database.py   # Подключение к БД (например PostgreSQL)
│   │   │   └── models.py     # SQLAlchemy модели (пользователи, сообщения, задачи)
│   │   ├── services/
│   │   │   ├── tasks.py      # Логика постановки задач в очередь
│   │   │   └── users.py      # Работа с пользователями (если нужно)
│   │   └── utils/
│   │       └── logger.py     # Общий логгер
│   ├── tests/                # Тесты для FastAPI
│   ├── requirements.txt
│   └── Dockerfile
│
├── ai_worker/                # ⚙️ Микросервис — AI Worker
│   ├── worker/
│   │   ├── main.py           # Точка входа Celery/RQ воркера
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   └── ai_tasks.py   # Функции обработки задач (вызов OpenAI API)
│   │   ├── core/
│   │   │   ├── config.py     # Настройки брокера, API-ключей
│   │   │   └── openai_client.py # Взаимодействие с OpenAI / локальной LLM
│   │   └── utils/
│   │       └── logger.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── telegram_bot/             # 💬 Telegram Bot (Aiogram)
│   ├── bot/
│   │   ├── main.py           # Точка входа бота
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── start.py      # /start, приветствие
│   │   │   ├── chat.py       # Основная логика общения
│   │   │   └── help.py
│   │   ├── services/
│   │   │   ├── api_client.py # Общение с FastAPI (HTTP-запросы)
│   │   │   ├── polling.py    # Проверка статуса задач (если без webhook)
│   │   │   └── notifier.py   # Отправка сообщений пользователю
│   │   ├── core/
│   │   │   ├── config.py     # Токен бота, адрес API
│   │   │   └── middleware.py # (опционально) логирование, антиспам
│   │   └── utils/
│   │       └── formatting.py # Форматирование ответов
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml         # 🐳 оркестрация всех сервисов
├── .env                       # Общие переменные окружения (API-ключи, Redis URL)
├── README.md
```

