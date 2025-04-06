#!/usr/bin/env python
"""
Скрипт для создания новой базы данных с нуля с правильной схемой.
Включает дополнительные поля для будущих расширений.
"""

import sqlite3
import os
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("db_creation.log")
    ]
)
logger = logging.getLogger("db_creation")

# Путь к новой базе данных
DB_PATH = "full_api_new.db"

# Если файл базы данных уже существует, создаем резервную копию
if os.path.exists(DB_PATH):
    backup_name = f"full_api_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    import shutil
    shutil.copy2(DB_PATH, backup_name)
    logger.info(f"Создана резервная копия базы данных: {backup_name}")
    os.remove(DB_PATH)
    logger.info(f"Старый файл базы данных удален")

# Схемы таблиц с дополнительными полями для расширения
SCHEMAS = {
    "organizations": """
    CREATE TABLE organizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL UNIQUE,
        description TEXT,
        org_type TEXT NOT NULL CHECK(org_type IN ('board', 'holding', 'legal_entity', 'location')),
        is_active INTEGER NOT NULL DEFAULT 1,
        parent_id INTEGER,
        ckp TEXT,
        inn TEXT,
        kpp TEXT,
        legal_address TEXT,
        physical_address TEXT,
        extra_field1 TEXT,
        extra_field2 TEXT,
        extra_field3 TEXT,
        extra_int1 INTEGER,
        extra_int2 INTEGER,
        extra_date1 DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_id) REFERENCES organizations(id)
    );

    -- Триггер для автоматического обновления даты изменения
    CREATE TRIGGER IF NOT EXISTS update_organization_timestamp 
    AFTER UPDATE ON organizations
    FOR EACH ROW
    BEGIN
        UPDATE organizations SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;

    -- Индексы для оптимизации запросов
    CREATE INDEX IF NOT EXISTS idx_organizations_parent_id ON organizations(parent_id);
    CREATE INDEX IF NOT EXISTS idx_organizations_org_type ON organizations(org_type);
    """,

    "divisions": """
    CREATE TABLE divisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL UNIQUE,
        description TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        organization_id INTEGER NOT NULL,
        parent_id INTEGER,
        ckp TEXT,
        extra_field1 TEXT,
        extra_field2 TEXT,
        extra_field3 TEXT,
        extra_int1 INTEGER,
        extra_int2 INTEGER,
        extra_date1 DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (organization_id) REFERENCES organizations(id),
        FOREIGN KEY (parent_id) REFERENCES divisions(id)
    );

    -- Триггер для автоматического обновления даты изменения
    CREATE TRIGGER IF NOT EXISTS update_division_timestamp 
    AFTER UPDATE ON divisions
    FOR EACH ROW
    BEGIN
        UPDATE divisions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;

    -- Индексы для оптимизации запросов
    CREATE INDEX IF NOT EXISTS idx_divisions_organization_id ON divisions(organization_id);
    CREATE INDEX IF NOT EXISTS idx_divisions_parent_id ON divisions(parent_id);
    """,

    "sections": """
    CREATE TABLE sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL UNIQUE,
        description TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        ckp TEXT,
        extra_field1 TEXT,
        extra_field2 TEXT,
        extra_field3 TEXT,
        extra_int1 INTEGER,
        extra_int2 INTEGER,
        extra_date1 DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Триггер для автоматического обновления даты изменения
    CREATE TRIGGER IF NOT EXISTS update_section_timestamp 
    AFTER UPDATE ON sections
    FOR EACH ROW
    BEGIN
        UPDATE sections SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;
    """,

    "division_sections": """
    CREATE TABLE division_sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        division_id INTEGER NOT NULL,
        section_id INTEGER NOT NULL,
        is_primary INTEGER NOT NULL DEFAULT 1,
        extra_field1 TEXT,
        extra_field2 TEXT,
        extra_field3 TEXT,
        extra_int1 INTEGER,
        extra_int2 INTEGER,
        extra_date1 DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (division_id) REFERENCES divisions(id),
        FOREIGN KEY (section_id) REFERENCES sections(id),
        UNIQUE(division_id, section_id)
    );

    -- Индексы для оптимизации запросов
    CREATE INDEX IF NOT EXISTS idx_division_sections_division_id ON division_sections(division_id);
    CREATE INDEX IF NOT EXISTS idx_division_sections_section_id ON division_sections(section_id);
    """,

    "functions": """
    CREATE TABLE functions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL UNIQUE,
        description TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        extra_field1 TEXT,
        extra_field2 TEXT,
        extra_field3 TEXT,
        extra_int1 INTEGER,
        extra_int2 INTEGER,
        extra_date1 DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Триггер для автоматического обновления даты изменения
    CREATE TRIGGER IF NOT EXISTS update_function_timestamp 
    AFTER UPDATE ON functions
    FOR EACH ROW
    BEGIN
        UPDATE functions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;
    """,

    "section_functions": """
    CREATE TABLE section_functions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        section_id INTEGER NOT NULL,
        function_id INTEGER NOT NULL,
        is_primary INTEGER NOT NULL DEFAULT 1,
        extra_field1 TEXT,
        extra_field2 TEXT,
        extra_field3 TEXT,
        extra_int1 INTEGER,
        extra_int2 INTEGER,
        extra_date1 DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (section_id) REFERENCES sections(id),
        FOREIGN KEY (function_id) REFERENCES functions(id),
        UNIQUE(section_id, function_id)
    );

    -- Индексы для оптимизации запросов
    CREATE INDEX IF NOT EXISTS idx_section_functions_section_id ON section_functions(section_id);
    CREATE INDEX IF NOT EXISTS idx_section_functions_function_id ON section_functions(function_id);
    """,

    "positions": """
    CREATE TABLE positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL UNIQUE,
        description TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        function_id INTEGER,
        extra_field1 TEXT,
        extra_field2 TEXT,
        extra_field3 TEXT,
        extra_int1 INTEGER,
        extra_int2 INTEGER,
        extra_date1 DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (function_id) REFERENCES functions(id)
    );

    -- Триггер для автоматического обновления даты изменения
    CREATE TRIGGER IF NOT EXISTS update_position_timestamp 
    AFTER UPDATE ON positions
    FOR EACH ROW
    BEGIN
        UPDATE positions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;

    -- Индексы для оптимизации запросов
    CREATE INDEX IF NOT EXISTS idx_positions_function_id ON positions(function_id);
    """,

    "staff": """
    CREATE TABLE staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        middle_name TEXT,
        phone TEXT,
        description TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        organization_id INTEGER,  -- Юридическое лицо (опционально)
        primary_organization_id INTEGER, -- Основное юридическое лицо
        extra_field1 TEXT,
        extra_field2 TEXT,
        extra_field3 TEXT,
        extra_int1 INTEGER,
        extra_int2 INTEGER,
        extra_date1 DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (organization_id) REFERENCES organizations(id),
        FOREIGN KEY (primary_organization_id) REFERENCES organizations(id)
    );

    -- Триггер для автоматического обновления даты изменения
    CREATE TRIGGER IF NOT EXISTS update_staff_timestamp 
    AFTER UPDATE ON staff
    FOR EACH ROW
    BEGIN
        UPDATE staff SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;

    -- Индексы для оптимизации запросов
    CREATE INDEX IF NOT EXISTS idx_staff_organization_id ON staff(organization_id);
    CREATE INDEX IF NOT EXISTS idx_staff_primary_organization_id ON staff(primary_organization_id);
    CREATE INDEX IF NOT EXISTS idx_staff_email ON staff(email);
    CREATE INDEX IF NOT EXISTS idx_staff_name ON staff(last_name, first_name);
    """,

    "staff_positions": """
    CREATE TABLE staff_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id INTEGER NOT NULL,
        position_id INTEGER NOT NULL,
        division_id INTEGER,
        location_id INTEGER,  -- Физическая локация, где работает сотрудник
        is_primary INTEGER NOT NULL DEFAULT 1,
        is_active INTEGER NOT NULL DEFAULT 1,
        start_date DATE NOT NULL DEFAULT CURRENT_DATE,
        end_date DATE,
        extra_field1 TEXT,
        extra_field2 TEXT,
        extra_field3 TEXT,
        extra_int1 INTEGER,
        extra_int2 INTEGER,
        extra_date1 DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (staff_id) REFERENCES staff(id),
        FOREIGN KEY (position_id) REFERENCES positions(id),
        FOREIGN KEY (division_id) REFERENCES divisions(id),
        FOREIGN KEY (location_id) REFERENCES organizations(id)
    );

    -- Триггер для автоматического обновления даты изменения
    CREATE TRIGGER IF NOT EXISTS update_staff_position_timestamp 
    AFTER UPDATE ON staff_positions
    FOR EACH ROW
    BEGIN
        UPDATE staff_positions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;

    -- Индексы для оптимизации запросов
    CREATE INDEX IF NOT EXISTS idx_staff_positions_staff_id ON staff_positions(staff_id);
    CREATE INDEX IF NOT EXISTS idx_staff_positions_position_id ON staff_positions(position_id);
    CREATE INDEX IF NOT EXISTS idx_staff_positions_division_id ON staff_positions(division_id);
    CREATE INDEX IF NOT EXISTS idx_staff_positions_location_id ON staff_positions(location_id);
    CREATE INDEX IF NOT EXISTS idx_staff_positions_is_primary ON staff_positions(is_primary);
    CREATE INDEX IF NOT EXISTS idx_staff_positions_is_active ON staff_positions(is_active);
    CREATE INDEX IF NOT EXISTS idx_staff_positions_dates ON staff_positions(start_date, end_date);
    """,

    "staff_locations": """
    CREATE TABLE staff_locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id INTEGER NOT NULL,
        location_id INTEGER NOT NULL,
        is_current INTEGER NOT NULL DEFAULT 1,
        date_from DATE NOT NULL DEFAULT CURRENT_DATE,
        date_to DATE,
        extra_field1 TEXT,
        extra_field2 TEXT,
        extra_field3 TEXT,
        extra_int1 INTEGER,
        extra_int2 INTEGER,
        extra_date1 DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (staff_id) REFERENCES staff(id),
        FOREIGN KEY (location_id) REFERENCES organizations(id)
    );

    -- Триггер для автоматического обновления даты изменения
    CREATE TRIGGER IF NOT EXISTS update_staff_location_timestamp 
    AFTER UPDATE ON staff_locations
    FOR EACH ROW
    BEGIN
        UPDATE staff_locations SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;

    -- Индексы для оптимизации запросов
    CREATE INDEX IF NOT EXISTS idx_staff_locations_staff_id ON staff_locations(staff_id);
    CREATE INDEX IF NOT EXISTS idx_staff_locations_location_id ON staff_locations(location_id);
    CREATE INDEX IF NOT EXISTS idx_staff_locations_is_current ON staff_locations(is_current);
    CREATE INDEX IF NOT EXISTS idx_staff_locations_dates ON staff_locations(date_from, date_to);
    """,

    "staff_functions": """
    CREATE TABLE staff_functions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id INTEGER NOT NULL,
        function_id INTEGER NOT NULL,
        commitment_percent INTEGER DEFAULT 100,
        is_primary INTEGER NOT NULL DEFAULT 1,
        date_from DATE NOT NULL DEFAULT CURRENT_DATE,
        date_to DATE,
        extra_field1 TEXT,
        extra_field2 TEXT,
        extra_field3 TEXT,
        extra_int1 INTEGER,
        extra_int2 INTEGER,
        extra_date1 DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (staff_id) REFERENCES staff(id),
        FOREIGN KEY (function_id) REFERENCES functions(id)
    );

    -- Триггер для автоматического обновления даты изменения
    CREATE TRIGGER IF NOT EXISTS update_staff_function_timestamp 
    AFTER UPDATE ON staff_functions
    FOR EACH ROW
    BEGIN
        UPDATE staff_functions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;

    -- Индексы для оптимизации запросов
    CREATE INDEX IF NOT EXISTS idx_staff_functions_staff_id ON staff_functions(staff_id);
    CREATE INDEX IF NOT EXISTS idx_staff_functions_function_id ON staff_functions(function_id);
    CREATE INDEX IF NOT EXISTS idx_staff_functions_is_primary ON staff_functions(is_primary);
    CREATE INDEX IF NOT EXISTS idx_staff_functions_dates ON staff_functions(date_from, date_to);
    """,

    "functional_relations": """
    CREATE TABLE functional_relations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        manager_id INTEGER NOT NULL,
        subordinate_id INTEGER NOT NULL,
        relation_type TEXT NOT NULL CHECK(relation_type IN ('functional', 'administrative', 'project', 'territorial', 'mentoring', 'strategic', 'governance', 'advisory', 'supervisory')),
        description TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        start_date DATE NOT NULL DEFAULT CURRENT_DATE,
        end_date DATE,
        extra_field1 TEXT,
        extra_field2 TEXT,
        extra_field3 TEXT,
        extra_int1 INTEGER,
        extra_int2 INTEGER,
        extra_date1 DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (manager_id) REFERENCES staff(id),
        FOREIGN KEY (subordinate_id) REFERENCES staff(id)
    );

    -- Триггер для автоматического обновления даты изменения
    CREATE TRIGGER IF NOT EXISTS update_functional_relation_timestamp 
    AFTER UPDATE ON functional_relations
    FOR EACH ROW
    BEGIN
        UPDATE functional_relations SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;

    -- Индексы для оптимизации запросов
    CREATE INDEX IF NOT EXISTS idx_functional_relations_manager_id ON functional_relations(manager_id);
    CREATE INDEX IF NOT EXISTS idx_functional_relations_subordinate_id ON functional_relations(subordinate_id);
    CREATE INDEX IF NOT EXISTS idx_functional_relations_relation_type ON functional_relations(relation_type);
    CREATE INDEX IF NOT EXISTS idx_functional_relations_dates ON functional_relations(start_date, end_date);
    """
}

def create_database():
    """Создает новую базу данных с расширенной схемой таблиц"""
    logger.info(f"Создание новой базы данных {DB_PATH}...")
    
    # Создаем соединение с базой данных
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Включаем поддержку foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Создаем таблицы
    for table_name, schema in SCHEMAS.items():
        logger.info(f"Создание таблицы {table_name}...")
        try:
            cursor.executescript(schema)
            logger.info(f"Таблица {table_name} успешно создана")
        except Exception as e:
            logger.error(f"Ошибка при создании таблицы {table_name}: {str(e)}")
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
    
    logger.info("База данных успешно создана")

if __name__ == "__main__":
    create_database() 