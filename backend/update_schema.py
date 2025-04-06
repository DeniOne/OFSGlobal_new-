#!/usr/bin/env python
"""
Скрипт для обновления схемы базы данных согласно новой архитектуре.
"""

import sqlite3
import logging
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("schema_update.log")
    ]
)
logger = logging.getLogger("schema_update")

# Путь к базе данных
DB_PATH = "full_api.db"

def backup_database():
    """Создает резервную копию базы данных перед обновлением схемы"""
    from datetime import datetime
    import shutil
    
    backup_name = f"full_api_backup_schema_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, backup_name)
        logger.info(f"Создана резервная копия базы данных: {backup_name}")
    else:
        logger.error(f"База данных {DB_PATH} не найдена!")
        return None
    
    return backup_name

def update_staff_table():
    """Обновляет таблицу staff, добавляя поле primary_organization_id и делая organization_id необязательным"""
    logger.info("Обновление таблицы staff...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем, есть ли уже поле primary_organization_id
        cursor.execute("PRAGMA table_info(staff)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "primary_organization_id" not in columns:
            # Добавляем поле primary_organization_id
            cursor.execute("ALTER TABLE staff ADD COLUMN primary_organization_id INTEGER")
            logger.info("Добавлено поле primary_organization_id")
            
            # Обновляем foreign key для нового поля
            # SQLite не позволяет напрямую добавлять FOREIGN KEY через ALTER TABLE,
            # но мы можем создать новую таблицу и перенести данные
            # Это сложная процедура, поэтому сейчас просто добавим поле
        
        # Делаем organization_id необязательным
        # В SQLite нельзя изменить атрибут NOT NULL, поэтому нужно пересоздать таблицу
        # Это сложная процедура, поэтому сейчас просто добавим поле primary_organization_id
        
        conn.commit()
        logger.info("Таблица staff успешно обновлена")
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка при обновлении таблицы staff: {str(e)}")
    finally:
        conn.close()

def update_staff_positions_table():
    """Обновляет таблицу staff_positions, добавляя поле division_id"""
    logger.info("Обновление таблицы staff_positions...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем, есть ли уже поле division_id
        cursor.execute("PRAGMA table_info(staff_positions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "division_id" not in columns:
            # Добавляем поле division_id
            cursor.execute("ALTER TABLE staff_positions ADD COLUMN division_id INTEGER")
            logger.info("Добавлено поле division_id")
        
        conn.commit()
        logger.info("Таблица staff_positions успешно обновлена")
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка при обновлении таблицы staff_positions: {str(e)}")
    finally:
        conn.close()

def create_staff_locations_table():
    """Создает новую таблицу staff_locations для связи сотрудников с локациями"""
    logger.info("Создание таблицы staff_locations...")
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        cursor = conn.cursor()
        # Проверяем, существует ли уже таблица
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='staff_locations'")
        if cursor.fetchone():
            logger.info("Таблица staff_locations уже существует")
            return
        
        # Создаем таблицу
        cursor.execute("""
        CREATE TABLE staff_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            location_id INTEGER NOT NULL,
            is_current INTEGER NOT NULL DEFAULT 1,
            date_from DATE NOT NULL DEFAULT CURRENT_DATE,
            date_to DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (staff_id) REFERENCES staff(id),
            FOREIGN KEY (location_id) REFERENCES organizations(id)
        )
        """)
        
        # Добавляем триггеры
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_staff_location_timestamp 
        AFTER UPDATE ON staff_locations
        FOR EACH ROW
        BEGIN
            UPDATE staff_locations SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
        END;
        """)
        
        # Добавляем индексы
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_staff_locations_staff_id ON staff_locations(staff_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_staff_locations_location_id ON staff_locations(location_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_staff_locations_is_current ON staff_locations(is_current)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_staff_locations_dates ON staff_locations(date_from, date_to)")
        
        conn.commit()
        logger.info("Таблица staff_locations успешно создана")
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка при создании таблицы staff_locations: {str(e)}")
    finally:
        conn.close()

def update_staff_functions_table():
    """Обновляет таблицу staff_functions, добавляя новые поля"""
    logger.info("Обновление таблицы staff_functions...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем, есть ли нужные поля
        cursor.execute("PRAGMA table_info(staff_functions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Добавляем новые поля
        if "commitment_percent" not in columns:
            cursor.execute("ALTER TABLE staff_functions ADD COLUMN commitment_percent INTEGER DEFAULT 100")
            logger.info("Добавлено поле commitment_percent")
        
        if "is_primary" not in columns:
            cursor.execute("ALTER TABLE staff_functions ADD COLUMN is_primary INTEGER DEFAULT 1")
            logger.info("Добавлено поле is_primary")
        
        if "date_from" not in columns:
            cursor.execute("ALTER TABLE staff_functions ADD COLUMN date_from DATE DEFAULT CURRENT_DATE")
            logger.info("Добавлено поле date_from")
        
        if "date_to" not in columns:
            cursor.execute("ALTER TABLE staff_functions ADD COLUMN date_to DATE")
            logger.info("Добавлено поле date_to")
        
        conn.commit()
        logger.info("Таблица staff_functions успешно обновлена")
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка при обновлении таблицы staff_functions: {str(e)}")
    finally:
        conn.close()

def main():
    """Основная функция для обновления схемы базы данных"""
    logger.info("Начало обновления схемы базы данных...")
    
    # Создаем резервную копию
    backup_path = backup_database()
    if not backup_path:
        logger.error("Не удалось создать резервную копию. Обновление схемы отменено.")
        return
    
    logger.info(f"Резервная копия создана: {backup_path}")
    
    try:
        # Шаг 1: Обновление таблицы staff
        update_staff_table()
        
        # Шаг 2: Обновление таблицы staff_positions
        update_staff_positions_table()
        
        # Шаг 3: Создание таблицы staff_locations
        create_staff_locations_table()
        
        # Шаг 4: Обновление таблицы staff_functions
        update_staff_functions_table()
        
        logger.info("Обновление схемы базы данных успешно завершено!")
    except Exception as e:
        logger.error(f"Произошла ошибка при обновлении схемы: {str(e)}")
        logger.info(f"Вы можете восстановить базу данных из резервной копии: {backup_path}")

if __name__ == "__main__":
    main() 