from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.organization import Organization, OrgType
from app.db.base_class import Base

# Создаем соединение с базой данных
# ВНИМАНИЕ: URL должен соответствовать URL в настройках приложения
SQLALCHEMY_DATABASE_URL = "sqlite:///./new_app.db"  # Новая база данных!

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создаем таблицы в базе данных
print("Создаем таблицы в базе данных...")
from app.models.organization import Organization
# Создаем только таблицу organizations
Base.metadata.create_all(engine, tables=[Organization.__table__])

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем сессию
db = SessionLocal()

try:
    # Создаем организацию
    new_org = Organization(
        name="ОФС Глобал Тест",
        code="OFST",
        description="Тестовая организация",
        org_type=OrgType.HOLDING,
        is_active=True
    )
    
    # Добавляем в БД и коммитим
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    
    print("Организация успешно создана!")
    print(f"ID: {new_org.id}")
    print(f"Название: {new_org.name}")
    print(f"Тип: {new_org.org_type}")
    
except Exception as e:
    print(f"Ошибка: {e}")
    db.rollback()
    
finally:
    db.close() 