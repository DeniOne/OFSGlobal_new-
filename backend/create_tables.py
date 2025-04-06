import asyncio
from app.db.session import engine
from app.db.base import Base
from app.models import *  # Импортирует все модели

async def create_tables():
    # Создаем все таблицы
    async with engine.begin() as conn:
        print("🗑️ Удаляем старые таблицы...")
        await conn.run_sync(Base.metadata.drop_all)
        
        print("🏗️ Создаем новые таблицы на основе моделей...")
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Все таблицы успешно созданы!")
    
    # Закрываем соединение
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables()) 