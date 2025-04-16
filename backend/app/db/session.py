# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
import asyncio
from contextlib import asynccontextmanager

# Синхронный движок для всех операций
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=settings.SQLALCHEMY_ECHO,
    connect_args={
        "client_encoding": "utf8"
    }
)

# Синхронная фабрика сессий
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Асинхронная сессия для FastAPI (фактически обёртка над синхронной)
@asynccontextmanager
async def get_db():
    """Зависимость для получения псевдо-асинхронной сессии базы данных."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# Синхронная сессия для CRUD операций
def get_sync_db() -> Session:
    """Получение синхронной сессии для CRUD операций."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close() 