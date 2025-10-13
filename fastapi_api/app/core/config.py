from dotenv import load_dotenv
import os


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user_project:admin123@localhost:5432/project_db")
URL_REDIS = os.getenv("URL_REDIS", "redis://:admin123@localhost:6379/0")