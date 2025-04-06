"""
Скрипт для создания всех таблиц базы данных напрямую.
"""
import os
import psycopg2
import time
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, Boolean, Text, DateTime, func
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Параметры подключения к БД
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'ofs_db_new'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost')
}

# Строка подключения SQLAlchemy
DB_URI = f"postgresql://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}/{DB_PARAMS['dbname']}"

def create_tables():
    """Создает все необходимые таблицы в базе данных."""
    
    # Подключаемся к БД
    print(f"🔄 Подключаемся к базе данных {DB_PARAMS['dbname']}...")
    engine = create_engine(DB_URI)
    
    try:
        # Создаем метаданные
        metadata = MetaData()
        
        # Определяем таблицы
        print("📝 Определяем схему таблиц...")
        
        # Таблица organizations
        organizations = Table(
            'organizations', metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('name', String(255), nullable=False, index=True),
            Column('legal_name', String(255)),
            Column('description', Text),
            Column('code', String(50)),
            Column('org_type', String(50), nullable=False),
            Column('is_active', Boolean, default=True),
            Column('created_at', DateTime, default=func.now()),
            Column('updated_at', DateTime, default=func.now(), onupdate=func.now()),
            Column('ckp', String(500))
        )
        
        # Таблица divisions (подразделения)
        divisions = Table(
            'divisions', metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('name', String(255), nullable=False, index=True),
            Column('organization_id', Integer, ForeignKey('organizations.id')),
            Column('parent_id', Integer, ForeignKey('divisions.id')),
            Column('code', String(50)),
            Column('is_active', Boolean, default=True),
            Column('created_at', DateTime, default=func.now()),
            Column('updated_at', DateTime, default=func.now(), onupdate=func.now()),
            Column('ckp', String(500))
        )
        
        # Таблица positions (должности)
        positions = Table(
            'positions', metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('name', String(255), nullable=False, index=True),
            Column('description', Text),
            Column('is_active', Boolean, default=True),
            Column('created_at', DateTime, default=func.now()),
            Column('updated_at', DateTime, default=func.now(), onupdate=func.now())
        )
        
        # Таблица staff (сотрудники)
        staff = Table(
            'staff', metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('first_name', String(255), nullable=False),
            Column('last_name', String(255), nullable=False),
            Column('middle_name', String(255)),
            Column('email', String(255), unique=True, index=True),
            Column('phone', String(50)),
            Column('division_id', Integer, ForeignKey('divisions.id')),
            Column('position_id', Integer, ForeignKey('positions.id')),
            Column('manager_id', Integer, ForeignKey('staff.id')),
            Column('photo_url', String(500)),
            Column('is_active', Boolean, default=True),
            Column('created_at', DateTime, default=func.now()),
            Column('updated_at', DateTime, default=func.now(), onupdate=func.now())
        )
        
        # Таблица functional_relations (функциональные отношения)
        functional_relations = Table(
            'functional_relations', metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('manager_id', Integer, ForeignKey('staff.id'), nullable=False),
            Column('subordinate_id', Integer, ForeignKey('staff.id'), nullable=False),
            Column('relation_type', String(50), index=True),
            Column('description', Text),
            Column('is_active', Boolean, default=True),
            Column('created_at', DateTime, default=func.now()),
            Column('updated_at', DateTime, default=func.now(), onupdate=func.now())
        )
        
        # Таблица sections (отделы)
        sections = Table(
            'sections', metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('name', String(255), nullable=False, index=True),
            Column('division_id', Integer, ForeignKey('divisions.id')),
            Column('code', String(50)),
            Column('is_active', Boolean, default=True),
            Column('created_at', DateTime, default=func.now()),
            Column('updated_at', DateTime, default=func.now(), onupdate=func.now()),
            Column('ckp', String(500))
        )
        
        # Таблица functions (функции)
        functions = Table(
            'functions', metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('name', String(255), nullable=False, index=True),
            Column('section_id', Integer, ForeignKey('sections.id')),
            Column('is_active', Boolean, default=True),
            Column('created_at', DateTime, default=func.now()),
            Column('updated_at', DateTime, default=func.now(), onupdate=func.now()),
            Column('ckp', String(500))
        )
        
        # Таблица staff_functions (связь сотрудников с функциями)
        staff_functions = Table(
            'staff_functions', metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('staff_id', Integer, ForeignKey('staff.id'), nullable=False),
            Column('function_id', Integer, ForeignKey('functions.id'), nullable=False),
            Column('is_primary', Boolean, default=False),
            Column('is_active', Boolean, default=True),
            Column('created_at', DateTime, default=func.now()),
            Column('updated_at', DateTime, default=func.now(), onupdate=func.now())
        )
        
        # Удаляем существующие таблицы если они есть
        print("🗑️ Удаляем существующие таблицы...")
        metadata.drop_all(engine)
        
        # Создаем таблицы
        print("🏗️ Создаем новые таблицы...")
        metadata.create_all(engine)
        
        print("✅ Все таблицы успешно созданы!")
        
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    create_tables() 