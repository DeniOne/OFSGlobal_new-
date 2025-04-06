import sqlite3
import logging
import sys
import random
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("staff_functions_creation")

DB_PATH = "full_api_new.db"

def get_db_connection():
    """Создает подключение к базе данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_staff():
    """Получает список всех сотрудников"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, first_name, last_name FROM staff")
    staff = cursor.fetchall()
    
    conn.close()
    return staff

def get_all_functions():
    """Получает список всех функций"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, code FROM functions")
    functions = cursor.fetchall()
    
    conn.close()
    return functions

def check_existing_staff_functions():
    """Проверяет существующие связи сотрудников с функциями"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM staff_functions")
    count = cursor.fetchone()[0]
    
    conn.close()
    return count > 0

def create_staff_functions():
    """Создает связи между сотрудниками и функциями"""
    logger.info("Создание функциональных обязанностей сотрудников...")
    
    # Проверяем, есть ли уже связи
    if check_existing_staff_functions():
        logger.info("Функциональные обязанности уже созданы")
        return
    
    # Получаем сотрудников и функции
    staff = get_all_staff()
    functions = get_all_functions()
    
    if not staff or not functions:
        logger.warning("Нет сотрудников или функций для создания связей")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Для каждого сотрудника создаем 1-3 связи с функциями
    for employee in staff:
        # Выбираем случайное количество функций для сотрудника (1-3)
        num_functions = random.randint(1, 3)
        selected_functions = random.sample(functions, min(num_functions, len(functions)))
        
        # Первая функция будет основной
        is_primary = True
        
        for function in selected_functions:
            # Определяем случайный процент занятости
            if is_primary:
                commitment_percent = random.randint(50, 100)
            else:
                commitment_percent = random.randint(10, 50)
            
            # Вычисляем случайную дату начала (до 2 лет назад)
            days_ago = random.randint(0, 365 * 2)
            start_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            # Для 20% должностей устанавливаем дату окончания
            end_date = None
            if random.random() < 0.2:
                future_days = random.randint(30, 365)
                end_date = (datetime.now() + timedelta(days=future_days)).strftime("%Y-%m-%d")
            
            # Создаем связь
            cursor.execute(
                """
                INSERT INTO staff_functions (
                    staff_id, function_id, commitment_percent, is_primary, date_from, date_to
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    employee["id"],
                    function["id"],
                    commitment_percent,
                    1 if is_primary else 0,
                    start_date,
                    end_date
                )
            )
            
            logger.info(f"Создана функциональная обязанность: Сотрудник {employee['first_name']} {employee['last_name']} -> {function['name']} ({commitment_percent}%)")
            
            # Следующие функции уже не основные
            is_primary = False
    
    conn.commit()
    conn.close()
    
    logger.info("Создание функциональных обязанностей завершено")

def main():
    try:
        create_staff_functions()
    except Exception as e:
        logger.error(f"Ошибка при создании функциональных обязанностей: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 