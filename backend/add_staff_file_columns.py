#!/usr/bin/env python
"""
Скрипт для добавления столбцов photo_path и document_paths в таблицу staff.
"""
import sqlite3
import logging
import sys
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("staff_file_columns.log")
    ]
)
logger = logging.getLogger(__name__)

# Поиск пути к файлу базы данных
def find_db_file():
    """Ищет файл базы данных в текущей и родительской директориях"""
    # Варианты имен файлов БД
    db_names = ["full_api.db", "full_api_new.db"]
    
    # Проверяем текущую директорию
    for db_name in db_names:
        if os.path.exists(db_name):
            return db_name
    
    # Проверяем родительскую директорию
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for db_name in db_names:
        parent_path = os.path.join(parent_dir, db_name)
        if os.path.exists(parent_path):
            return parent_path
    
    return None

def add_file_columns():
    """Добавляет столбцы для файлов в таблицу staff"""
    try:
        # Находим файл БД
        db_path = find_db_file()
        if not db_path:
            logger.error("База данных не найдена")
            return False
        
        logger.info(f"Используется база данных: {db_path}")
        
        # Открываем соединение с базой данных
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Проверяем существует ли таблица staff
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='staff'")
        if not cursor.fetchone():
            logger.error("Таблица staff не найдена в базе данных")
            conn.close()
            return False
        
        # Проверяем наличие колонок
        cursor.execute("PRAGMA table_info(staff)")
        columns = {column['name'] for column in cursor.fetchall()}
        
        # Добавляем столбец photo_path, если его нет
        if 'photo_path' not in columns:
            logger.info("Добавление столбца photo_path в таблицу staff")
            cursor.execute("ALTER TABLE staff ADD COLUMN photo_path TEXT")
        else:
            logger.info("Столбец photo_path уже существует")
        
        # Добавляем столбец document_paths, если его нет
        if 'document_paths' not in columns:
            logger.info("Добавление столбца document_paths в таблицу staff")
            cursor.execute("ALTER TABLE staff ADD COLUMN document_paths TEXT DEFAULT '{}'")
        else:
            logger.info("Столбец document_paths уже существует")
        
        # Применяем изменения
        conn.commit()
        logger.info("Столбцы для файлов успешно добавлены в таблицу staff")
        
        # Создаем каталоги для файлов, если они не существуют
        # Определяем корневую директорию проекта
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        uploads_dir = os.path.join(root_dir, "uploads", "staff")
        os.makedirs(uploads_dir, exist_ok=True)
        logger.info(f"Каталог {uploads_dir} создан")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при добавлении столбцов: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    logger.info("Запуск скрипта добавления столбцов для файлов")
    if add_file_columns():
        logger.info("Скрипт успешно выполнен")
    else:
        logger.error("Ошибка выполнения скрипта") 