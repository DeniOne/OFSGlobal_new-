import asyncio
from app.db.base import Base

def check_models():
    """
    Проверяет правильность инициализации моделей SQLAlchemy без обращения к базе данных.
    """
    try:
        # Просто обращаемся к метаданным - это заставит SQLAlchemy инициализировать все маппинги
        print("Инициализация моделей SQLAlchemy...")
        tables = Base.metadata.tables
        print(f"✅ Модели успешно инициализированы. Зарегистрировано {len(tables)} таблиц:")
        for table_name in tables:
            print(f"  - {table_name}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при инициализации моделей: {str(e)}")
        return False

if __name__ == "__main__":
    check_models() 