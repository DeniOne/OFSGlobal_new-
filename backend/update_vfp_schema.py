"""
Обновление схемы БД для добавления таблицы ЦКП (Ценный Конечный Продукт)
"""

import sqlite3
import logging
import json
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    filename='vfp_schema_update.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# SQL для создания таблицы ЦКП
VFP_SCHEMA = """
CREATE TABLE IF NOT EXISTS valuable_final_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL CHECK(
        entity_type IN ('board', 'director', 'division', 'section', 'function', 'organization')
    ),
    entity_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    metrics TEXT,  -- JSON с метриками для измерения
    status TEXT CHECK(
        status IN ('not_started', 'in_progress', 'completed', 'blocked', 'delayed')
    ),
    progress INTEGER CHECK(progress BETWEEN 0 AND 100),
    start_date DATE,
    target_date DATE,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ограничение уникальности для комбинации тип+id
    UNIQUE(entity_type, entity_id)
);

-- Триггер для автоматического обновления даты изменения
CREATE TRIGGER IF NOT EXISTS update_vfp_timestamp 
AFTER UPDATE ON valuable_final_products
FOR EACH ROW
BEGIN
    UPDATE valuable_final_products 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = OLD.id;
END;

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_vfp_entity ON valuable_final_products(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_vfp_status ON valuable_final_products(status);
"""

def update_schema(db_path='full_api_new.db'):
    """Обновляет схему БД, добавляя таблицу ЦКП"""
    try:
        # Создаём бэкап базы перед изменениями
        backup_path = f"full_api_backup_vfp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        logging.info(f"Created backup at {backup_path}")

        # Подключаемся к БД
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Создаём таблицу
        cursor.executescript(VFP_SCHEMA)
        conn.commit()

        # Проверяем что таблица создалась
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='valuable_final_products'")
        if cursor.fetchone():
            logging.info("VFP table created successfully")
        else:
            logging.error("Failed to create VFP table")
            return False

        # Проверяем структуру таблицы
        cursor.execute("PRAGMA table_info(valuable_final_products)")
        columns = cursor.fetchall()
        logging.info(f"VFP table structure: {json.dumps([col[1] for col in columns], indent=2)}")

        return True

    except Exception as e:
        logging.error(f"Error updating schema: {str(e)}")
        return False

    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if update_schema():
        print("Schema updated successfully! Check vfp_schema_update.log for details.")
    else:
        print("Failed to update schema. Check vfp_schema_update.log for errors.") 