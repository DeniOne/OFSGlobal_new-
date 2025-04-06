import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.core.config import settings

# Создаем тестовый движок базы данных
test_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI.replace(settings.POSTGRES_DB, f"{settings.POSTGRES_DB}_test"),
    echo=True,
    future=True,
    connect_args={
        "timeout": 30,
        "command_timeout": 30,
        "server_settings": {
            "client_encoding": "UTF8"
        }
    }
)

# Создаем фабрику сессий
async_session = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Устанавливаем scope для event loop
pytest.asyncio_default_fixture_loop_scope = "function"

@pytest.fixture(scope="function")
def event_loop_policy():
    """Create and set a new event loop policy for tests."""
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    return policy

@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    Создает тестовую базу данных и возвращает сессию.
    Пересоздает базу для каждого теста.
    """
    # Создаем таблицы перед каждым тестом
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Создаем новую сессию для теста
    async with async_session() as session:
        async with session.begin():
            yield session
            # Откатываем изменения после теста
            await session.rollback()
    
    # Удаляем таблицы после теста
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) 