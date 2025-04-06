# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Асинхронный движок
async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=settings.SQLALCHEMY_ECHO,
    connect_args={
        "timeout": 30,
        "command_timeout": 30,
        "server_settings": {
            "client_encoding": "UTF8"
        }
    }
)

# Синхронный движок для CRUD операций
sync_engine = create_engine(
    settings.SYNC_SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=settings.SQLALCHEMY_ECHO,
    connect_args={
        "client_encoding": "UTF8"
    }
)

# Асинхронная фабрика сессий
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Синхронная фабрика сессий для CRUD
SessionLocal = sessionmaker(
    sync_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Асинхронная сессия для FastAPI
async def get_db() -> AsyncSession:
    """Зависимость для получения асинхронной сессии базы данных."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Синхронная сессия для CRUD операций
def get_sync_db() -> Session:
    """Получение синхронной сессии для CRUD операций."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close() 