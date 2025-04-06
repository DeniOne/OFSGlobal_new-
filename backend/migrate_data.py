#!/usr/bin/env python
"""
Скрипт для миграции данных из старой схемы в новую гибкую архитектуру.

Этот скрипт выполняет следующие шаги:
1. Обновляет существующих сотрудников, добавляя primary_organization_id
2. Создает связи staff_locations для всех сотрудников на основе их organization_id
3. Мигрирует существующие staff_positions с добавлением division_id
4. Создает staff_functions для сотрудников на основе их должностей

Запуск:
python migrate_data.py
"""

import sqlite3
import os
import sys
import logging
from datetime import datetime, date

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("migration.log")
    ]
)
logger = logging.getLogger("data_migration")

# Путь к базе данных
DB_PATH = "full_api.db"

def get_db_connection():
    """Создает соединение с базой данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def backup_database():
    """Создает резервную копию базы данных перед миграцией"""
    backup_name = f"full_api_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    if os.path.exists(DB_PATH):
        import shutil
        shutil.copy2(DB_PATH, backup_name)
        logger.info(f"Создана резервная копия базы данных: {backup_name}")
    else:
        logger.error(f"База данных {DB_PATH} не найдена!")
        sys.exit(1)
    
    return backup_name

def update_staff_with_primary_organization():
    """
    Обновляет таблицу сотрудников, добавляя primary_organization_id 
    на основе текущего organization_id
    """
    logger.info("Обновление сотрудников с primary_organization_id...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Получаем всех сотрудников
        cursor.execute("SELECT id, organization_id FROM staff")
        staff_list = cursor.fetchall()
        
        updated_count = 0
        for staff in staff_list:
            # Используем текущий organization_id как primary_organization_id
            cursor.execute(
                "UPDATE staff SET primary_organization_id = ? WHERE id = ?",
                (staff["organization_id"], staff["id"])
            )
            updated_count += 1
        
        conn.commit()
        logger.info(f"Обновлено {updated_count} записей сотрудников")
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка при обновлении сотрудников: {str(e)}")
    finally:
        conn.close()

def create_staff_locations():
    """
    Создает записи в таблице staff_locations для всех сотрудников
    на основе их organization_id
    """
    logger.info("Создание записей staff_locations...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Сначала получаем всех сотрудников
        cursor.execute("SELECT id, organization_id FROM staff")
        staff_list = cursor.fetchall()
        
        # Получаем локации
        cursor.execute("SELECT id FROM organizations WHERE org_type = 'location'")
        locations = [row["id"] for row in cursor.fetchall()]
        
        # Если локаций нет, создаем хотя бы одну по умолчанию
        default_location_id = None
        if not locations:
            # Находим первую организацию с типом "legal_entity"
            cursor.execute("SELECT id FROM organizations WHERE org_type = 'legal_entity' LIMIT 1")
            legal_entity = cursor.fetchone()
            
            if legal_entity:
                # Создаем локацию по умолчанию
                cursor.execute(
                    """
                    INSERT INTO organizations (name, code, description, org_type, parent_id)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        "Головной офис",
                        "HQ",
                        "Локация по умолчанию, созданная при миграции",
                        "location",
                        legal_entity["id"]
                    )
                )
                default_location_id = cursor.lastrowid
                logger.info(f"Создана локация по умолчанию с ID {default_location_id}")
            else:
                logger.warning("Не найдено ни одной организации с типом 'legal_entity'. Не удалось создать локацию по умолчанию.")
        else:
            default_location_id = locations[0]
        
        if default_location_id:
            # Создаем записи staff_locations для каждого сотрудника
            created_count = 0
            for staff in staff_list:
                cursor.execute(
                    """
                    INSERT INTO staff_locations (
                        staff_id, location_id, is_current, date_from
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        staff["id"],
                        default_location_id,
                        1,
                        date.today().isoformat()
                    )
                )
                created_count += 1
            
            conn.commit()
            logger.info(f"Создано {created_count} записей staff_locations")
        else:
            logger.error("Невозможно создать staff_locations: нет доступных локаций")
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка при создании staff_locations: {str(e)}")
    finally:
        conn.close()

def migrate_staff_positions():
    """
    Обновляет существующие записи staff_positions,
    добавляя division_id, если это возможно
    """
    logger.info("Обновление записей staff_positions...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Получаем связь должностей с департаментами через позиции
        cursor.execute(
            """
            SELECT p.id AS position_id, d.id AS division_id
            FROM positions p
            JOIN functions f ON p.function_id = f.id
            JOIN section_functions sf ON f.id = sf.function_id
            JOIN division_sections ds ON sf.section_id = ds.section_id
            JOIN divisions d ON ds.division_id = d.id
            """
        )
        position_division_map = {}
        for row in cursor.fetchall():
            position_id = row["position_id"]
            division_id = row["division_id"]
            
            # Если уже есть запись для этой должности, пропускаем
            if position_id in position_division_map:
                continue
                
            position_division_map[position_id] = division_id
        
        # Обновляем staff_positions
        cursor.execute("SELECT id, position_id FROM staff_positions")
        staff_positions = cursor.fetchall()
        
        updated_count = 0
        for sp in staff_positions:
            position_id = sp["position_id"]
            
            if position_id in position_division_map:
                division_id = position_division_map[position_id]
                cursor.execute(
                    "UPDATE staff_positions SET division_id = ? WHERE id = ?",
                    (division_id, sp["id"])
                )
                updated_count += 1
        
        conn.commit()
        logger.info(f"Обновлено {updated_count} записей staff_positions с division_id")
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка при обновлении staff_positions: {str(e)}")
    finally:
        conn.close()

def create_staff_functions():
    """
    Создает записи в таблице staff_functions на основе
    должностей сотрудников и их функций
    """
    logger.info("Создание записей staff_functions...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Получаем связь должностей с функциями
        cursor.execute(
            """
            SELECT sp.staff_id, p.function_id
            FROM staff_positions sp
            JOIN positions p ON sp.position_id = p.id
            WHERE p.function_id IS NOT NULL
            AND sp.is_primary = 1
            """
        )
        staff_function_relations = cursor.fetchall()
        
        created_count = 0
        for relation in staff_function_relations:
            staff_id = relation["staff_id"]
            function_id = relation["function_id"]
            
            # Проверяем, не существует ли уже такая связь
            cursor.execute(
                "SELECT id FROM staff_functions WHERE staff_id = ? AND function_id = ?",
                (staff_id, function_id)
            )
            
            if cursor.fetchone() is None:
                cursor.execute(
                    """
                    INSERT INTO staff_functions (
                        staff_id, function_id, commitment_percent, is_primary, date_from
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        staff_id,
                        function_id,
                        100,  # 100% загрузки по умолчанию
                        1,    # Основная функция
                        date.today().isoformat()
                    )
                )
                created_count += 1
        
        conn.commit()
        logger.info(f"Создано {created_count} записей staff_functions")
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка при создании staff_functions: {str(e)}")
    finally:
        conn.close()

def main():
    """Основная функция для выполнения миграции"""
    logger.info("Начало миграции данных...")
    
    # Создаем резервную копию
    backup_path = backup_database()
    logger.info(f"Резервная копия создана: {backup_path}")
    
    try:
        # Шаг 1: Обновление таблицы staff
        update_staff_with_primary_organization()
        
        # Шаг 2: Создание записей staff_locations
        create_staff_locations()
        
        # Шаг 3: Обновление staff_positions
        migrate_staff_positions()
        
        # Шаг 4: Создание staff_functions
        create_staff_functions()
        
        logger.info("Миграция данных успешно завершена!")
    except Exception as e:
        logger.error(f"Произошла ошибка при миграции: {str(e)}")
        logger.info(f"Вы можете восстановить базу данных из резервной копии: {backup_path}")
        sys.exit(1)

if __name__ == "__main__":
    main() 