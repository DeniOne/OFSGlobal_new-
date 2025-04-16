# Руководство по миграции с SQLite на PostgreSQL

## Обзор

Данное руководство описывает процесс миграции базы данных OFS Global API с SQLite на PostgreSQL. PostgreSQL предоставляет более надежную и масштабируемую систему управления базами данных, которая лучше подходит для производственной среды.

## Предварительные требования

1. **Установленный PostgreSQL** (рекомендуется версия 14+)
2. **Доступ к текущей базе данных SQLite**
3. **Python 3.10+**
4. **Библиотеки**:
   - SQLAlchemy 2.0+
   - psycopg2-binary (драйвер PostgreSQL для Python)
   - alembic (для миграций схемы)

## Шаг 1: Установка и настройка PostgreSQL

### Установка PostgreSQL на Windows

1. **Скачайте установщик** с [официального сайта](https://www.postgresql.org/download/windows/).
2. **Запустите установщик** и следуйте инструкциям.
3. **Запомните пароль** для пользователя `postgres`, который вы устанавливаете во время установки.
4. **Откройте pgAdmin** (устанавливается вместе с PostgreSQL) для управления базой данных.

### Создание базы данных и пользователя

1. **Подключитесь к серверу PostgreSQL** через pgAdmin или командную строку.
2. **Создайте новую базу данных**:
   ```sql
   CREATE DATABASE ofs_global;
   ```
3. **Создайте пользователя** для приложения:
   ```sql
   CREATE USER ofs_user WITH PASSWORD 'ваш_пароль';
   ```
4. **Предоставьте права** пользователю:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE ofs_global TO ofs_user;
   ```

## Шаг 2: Настройка SQLAlchemy и Alembic

### Установка необходимых библиотек

```bash
pip install sqlalchemy~=2.0.0 psycopg2-binary alembic
```

### Настройка SQLAlchemy

1. **Создайте файл конфигурации** `app/core/config.py`:
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://ofs_user:ваш_пароль@localhost/ofs_global"
    # Другие настройки приложения...
    
    class Config:
        env_file = ".env"

settings = Settings()
```

2. **Создайте файл подключения к БД** `app/db/session.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Создаем движок SQLAlchemy
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Функция-зависимость для FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Настройка Alembic для миграций

1. **Инициализация Alembic**:
```bash
alembic init alembic
```

2. **Настройка Alembic** в файле `alembic/env.py`:
```python
from app.db.session import Base
from app.core.config import settings

# Импортируйте все модели, чтобы Alembic мог их обнаружить
from app.models.organization import Organization
from app.models.division import Division
from app.models.section import Section
from app.models.position import Position
from app.models.staff import Staff
# ... другие модели ...

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata
```

## Шаг 3: Определение моделей SQLAlchemy

Создайте модели SQLAlchemy на основе существующей схемы SQLite. Пример модели:

```python
# app/models/organization.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.db.session import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    org_type = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

## Шаг 4: Создание миграции схемы

1. **Сгенерируйте скрипт миграции**:
```bash
alembic revision --autogenerate -m "initial_migration"
```

2. **Примените миграцию**:
```bash
alembic upgrade head
```

## Шаг 5: Миграция данных из SQLite в PostgreSQL

Создайте скрипт для миграции данных:

```python
# migrate_data.py
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from app.core.config import settings

def migrate_data():
    # Подключение к SQLite
    sqlite_conn = sqlite3.connect("backend/full_api.db")
    
    # Подключение к PostgreSQL
    pg_engine = create_engine(settings.DATABASE_URL)
    
    # Получение списка таблиц из SQLite
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", sqlite_conn)
    
    # Миграция каждой таблицы
    for table_name in tables['name']:
        if table_name != 'sqlite_sequence':  # Пропускаем служебные таблицы SQLite
            print(f"Migrating table {table_name}...")
            
            # Считываем данные из SQLite
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", sqlite_conn)
            
            if not df.empty:
                # Записываем данные в PostgreSQL
                df.to_sql(table_name, pg_engine, if_exists='append', index=False)
                
                # Обновляем последовательности (автоинкремент) в PostgreSQL
                if 'id' in df.columns:
                    max_id = df['id'].max()
                    pg_engine.execute(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), {max_id});")
                
            print(f"Migrated {len(df)} rows from {table_name}")
    
    sqlite_conn.close()
    print("Migration completed!")

if __name__ == "__main__":
    migrate_data()
```

## Шаг 6: Обновление приложения для работы с PostgreSQL

1. **Замените все прямые запросы SQLite** на использование SQLAlchemy ORM.
2. **Адаптируйте специфичные для SQLite функции** на аналоги PostgreSQL:
   - Замените `CURRENT_TIMESTAMP` на `NOW()`
   - Обновите синтаксис для работы с датами/временем
   - Замените использование `ROWID` на стандартный `id`

3. **Пример преобразования прямого запроса SQLite в ORM**:

До (SQLite):
```python
@app.get("/organizations/")
def get_organizations(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM organizations")
    orgs = cursor.fetchall()
    return orgs
```

После (SQLAlchemy ORM):
```python
@app.get("/organizations/")
def get_organizations(db: Session = Depends(get_db)):
    orgs = db.query(Organization).all()
    return orgs
```

## Шаг 7: Тестирование и устранение проблем

1. **Проверьте все эндпоинты API** после миграции.
2. **Проверьте специфичные запросы**, особенно включающие:
   - Сложные JOIN-ы
   - Оконные функции
   - Транзакции
   - Полнотекстовый поиск

3. **Оптимизация для PostgreSQL**:
   - Добавьте индексы для часто используемых полей
   - Настройте подходящие типы данных (используйте UUID, JSONB и т.д.)
   - Используйте преимущества PostgreSQL (например, материализованные представления)

## Шаг 8: Настройка бекапа PostgreSQL

1. **Регулярные дампы базы данных**:
```bash
pg_dump -U ofs_user -W -F t ofs_global > backup_$(date +%Y-%m-%d).tar
```

2. **Настройте автоматические резервные копии**:
```bash
# Добавьте в crontab (Linux/Mac)
0 0 * * * pg_dump -U ofs_user -W -F t ofs_global > /path/to/backups/backup_$(date +\%Y-\%m-\%d).tar
```

3. **Для Windows** можно использовать Планировщик задач с батником:
```batch
REM backup.bat
@echo off
SET PGPASSWORD=ваш_пароль
pg_dump -U ofs_user -F t ofs_global > D:\backups\backup_%date:~-4,4%-%date:~-7,2%-%date:~-10,2%.tar
```

## Дополнительные рекомендации

1. **Настройте правильные типы данных**:
   - Используйте `JSONB` для хранения JSON-данных вместо текста
   - Рассмотрите использование `UUID` вместо числовых ID для некоторых сущностей
   - Используйте `ENUM` типы для статусов и других ограниченных наборов значений

2. **Оптимизируйте индексы**:
   - Используйте индексы B-tree для столбцов в условиях WHERE и JOIN
   - Рассмотрите частичные индексы для больших таблиц
   - Используйте индексы GIN для полнотекстового поиска

3. **Мониторинг и обслуживание**:
   - Настройте регулярную очистку (VACUUM) базы данных
   - Настройте мониторинг производительности
   - Рассмотрите возможность использования Connection Pooling (pgBouncer)

## Заключение

Миграция с SQLite на PostgreSQL - важный шаг для повышения надежности, производительности и масштабируемости вашего приложения. Хотя процесс требует тщательного планирования и тестирования, преимущества использования полноценной РСУБД для производственной среды очевидны.

Не забудьте обновить документацию и инструкции по развертыванию для отражения новой архитектуры базы данных. 