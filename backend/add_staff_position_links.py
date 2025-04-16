import sqlite3
import logging
import random
from datetime import datetime, date, timedelta
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("add_links.log") # Лог будет писаться в add_links.log
    ]
)
logger = logging.getLogger("add_staff_pos_links")

# Путь к базе данных (убедись, что он правильный)
DB_PATH = "full_api_new.db"

def get_db_connection():
    """Создает соединение с базой данных"""
    db_full_path = os.path.join(os.path.dirname(__file__), DB_PATH)
    if not os.path.exists(db_full_path):
        logger.error(f"Файл базы данных {db_full_path} не найден!")
        raise FileNotFoundError(f"Database file not found: {db_full_path}")
    conn = sqlite3.connect(db_full_path)
    conn.row_factory = sqlite3.Row
    return conn

def random_date(start=date(2022, 1, 1), end=date.today()):
    """Генерирует случайную дату в указанном диапазоне"""
    try:
        # Убедимся, что end не раньше start
        if end < start:
            end = start
        delta = (end - start).days
        return start + timedelta(days=random.randint(0, delta))
    except Exception as e:
        logger.warning(f"Ошибка генерации случайной даты (start={start}, end={end}): {e}. Возвращаем сегодняшнюю.")
        return date.today()


def add_missing_staff_position_links():
    """Добавляет недостающие активные связи сотрудник-должность"""
    logger.info("Проверка и добавление связей сотрудник-должность...")
    conn = None
    added_links_count = 0
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Получаем ID всех сотрудников
        cursor.execute("SELECT id FROM staff")
        all_staff_ids = {row['id'] for row in cursor.fetchall()}
        if not all_staff_ids:
            logger.warning("В таблице 'staff' нет сотрудников. Нечего связывать.")
            return

        # 2. Получаем ID всех должностей
        cursor.execute("SELECT id FROM positions")
        all_position_ids = [row['id'] for row in cursor.fetchall()]
        if not all_position_ids:
            logger.warning("В таблице 'positions' нет должностей. Не с чем связывать.")
            return

        # 3. Получаем ID сотрудников, УЖЕ имеющих АКТИВНУЮ основную связь
        cursor.execute("""
            SELECT DISTINCT staff_id
            FROM staff_positions
            WHERE is_active = 1 AND is_primary = 1
        """)
        linked_staff_ids = {row['staff_id'] for row in cursor.fetchall()}
        logger.info(f"Найдено сотрудников: {len(all_staff_ids)}. Из них уже имеют активную основную связь: {len(linked_staff_ids)}")

        # 4. Определяем сотрудников без активной основной связи
        staff_to_link = all_staff_ids - linked_staff_ids
        logger.info(f"Сотрудников для добавления связи: {len(staff_to_link)}")

        if not staff_to_link:
            logger.info("Все сотрудники уже имеют активную основную связь.")
            return

        # 5. Добавляем связи для недостающих
        for staff_id in staff_to_link:
            try:
                position_id = random.choice(all_position_ids)
                # Генерируем дату в прошлом, но не раньше 2022 года
                start_date_pos = random_date(start=date(2022, 1, 1), end=date.today() - timedelta(days=1))
                division_id = None # Можно улучшить, выбирая случайное подразделение
                location_id = None # Можно улучшить, выбирая случайную локацию

                cursor.execute(
                    """
                    INSERT INTO staff_positions (
                        staff_id, position_id, division_id, location_id, is_primary,
                        is_active, start_date, end_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        staff_id,
                        position_id,
                        division_id,
                        location_id,
                        1,  # Считаем добавляемую связь основной
                        1,  # Связь активна (нет end_date)
                        start_date_pos.isoformat(),
                        None # end_date = NULL
                    )
                )
                logger.debug(f"Добавлена связь: Сотрудник ID {staff_id} -> Должность ID {position_id}")
                added_links_count += 1
            except sqlite3.IntegrityError as e:
                # Может возникнуть, если случайно пытаемся вставить дубликат staff_id/position_id, если там есть UNIQUE constraint
                logger.warning(f"Ошибка целостности при добавлении связи для сотрудника {staff_id}: {e}. Пропускаем.")
                # Не откатываем всю транзакцию, просто пропускаем эту запись
            except Exception as e:
                 logger.error(f"Неожиданная ошибка при добавлении связи для сотрудника {staff_id}: {e}")
                 # Здесь лучше откатить и прервать, чтобы не наделать делов
                 if conn: conn.rollback()
                 raise # Перевыбрасываем ошибку

        conn.commit() # Коммитим все успешные вставки
        logger.info(f"Успешно добавлено связей: {added_links_count}")

    except sqlite3.Error as e:
        logger.error(f"Ошибка SQLite при работе с базой данных: {e}")
        if conn:
            conn.rollback()
    except FileNotFoundError:
        # Ошибка уже залогирована в get_db_connection
        pass
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            logger.debug("Соединение с БД закрыто.")

if __name__ == "__main__":
    logger.info("=== ЗАПУСК СКРИПТА ДОБАВЛЕНИЯ СВЯЗЕЙ СОТРУДНИК-ДОЛЖНОСТЬ ===")
    add_missing_staff_position_links()
    logger.info("=== ЗАВЕРШЕНИЕ РАБОТЫ СКРИПТА ===")
