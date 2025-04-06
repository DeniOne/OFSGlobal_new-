#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для добавления недостающих столбцов в таблицу staff
Используется для обновления схемы базы данных без потери данных
"""

import sqlite3
import os
import sys
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('schema_update_staff.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Путь к базе данных
DB_PATH = 'full_api_new.db'

def create_backup():
    """Создает резервную копию базы данных перед внесением изменений"""
    try:
        backup_path = f'full_api_backup_before_staff_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        if os.path.exists(DB_PATH):
            with open(DB_PATH, 'rb') as src:
                with open(backup_path, 'wb') as dst:
                    dst.write(src.read())
            logger.info(f"Создана резервная копия базы данных: {backup_path}")
            return True
        else:
            logger.error(f"Файл базы данных {DB_PATH} не найден")
            return False
    except Exception as e:
        logger.error(f"Ошибка при создании резервной копии: {str(e)}")
        return False

def add_missing_columns():
    """Добавляет недостающие столбцы в таблицу staff"""
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Получаем информацию о существующих столбцах
        cursor.execute("PRAGMA table_info(staff)")
        columns = [column[1] for column in cursor.fetchall()]
        logger.info(f"Текущие столбцы таблицы staff: {', '.join(columns)}")
        
        # Список столбцов для добавления: имя, тип, nullable
        missing_columns = [
            ("location_id", "INTEGER", True),
            ("extra_int1", "INTEGER", True),  # Для actual_address, если его нет
        ]
        
        added_columns = []
        for column_name, column_type, nullable in missing_columns:
            if column_name not in columns:
                null_clause = "NULL" if nullable else "NOT NULL DEFAULT ''"
                query = f"ALTER TABLE staff ADD COLUMN {column_name} {column_type} {null_clause}"
                logger.info(f"Выполняется запрос: {query}")
                cursor.execute(query)
                added_columns.append(column_name)
                logger.info(f"Столбец {column_name} успешно добавлен")
        
        # Создаем индексы для новых столбцов
        if "location_id" in added_columns:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_staff_location_id ON staff(location_id)")
            logger.info("Создан индекс для столбца location_id")
        
        conn.commit()
        
        # Проверяем, что столбцы добавлены
        cursor.execute("PRAGMA table_info(staff)")
        new_columns = [column[1] for column in cursor.fetchall()]
        logger.info(f"Обновленные столбцы таблицы staff: {', '.join(new_columns)}")
        
        # Проверка на отсутствие столбцов
        for column_name, _, _ in missing_columns:
            if column_name not in new_columns:
                logger.warning(f"Столбец {column_name} не был добавлен!")
        
        conn.close()
        
        if not added_columns:
            logger.info("Все необходимые столбцы уже существуют в таблице staff")
        else:
            logger.info(f"Добавлены столбцы: {', '.join(added_columns)}")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при добавлении столбцов: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("=== Запуск скрипта обновления таблицы staff ===")
    
    # Создаем резервную копию
    if not create_backup():
        logger.error("Не удалось создать резервную копию. Обновление отменено.")
        sys.exit(1)
    
    # Добавляем недостающие столбцы
    if add_missing_columns():
        logger.info("Обновление таблицы staff успешно завершено")
    else:
        logger.error("Не удалось обновить таблицу staff")
        sys.exit(1) 