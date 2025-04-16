from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

# Получаем URL из переменных окружения или используем значение по умолчанию
# Конструируем URL из индивидуальных компонентов
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "111")
# URL-кодируем пароль для безопасного использования в URL
ENCODED_PASSWORD = quote_plus(DB_PASSWORD)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ofs_db_new")

# Для синхронного подключения
DATABASE_URL = f"postgresql://{DB_USER}:{ENCODED_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Для асинхронного подключения
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

print(f"DATABASE_URL (masking password): postgresql://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")
print(f"ASYNC_DATABASE_URL (masking password): postgresql+asyncpg://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Синхронный движок и сессия
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Асинхронный движок и сессия
async_engine = create_async_engine(ASYNC_DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=async_engine
)

# Базовый класс для моделей
Base = declarative_base()

# Функции для получения соединения
def get_db_sync():
    """
    Синхронная функция для получения соединения с БД
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_db_async():
    """
    Асинхронная функция для получения соединения с БД
    """
    async with AsyncSessionLocal() as db:
        yield db
