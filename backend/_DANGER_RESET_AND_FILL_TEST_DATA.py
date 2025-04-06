#!/usr/bin/env python
"""
Скрипт для заполнения новой базы данных тестовыми данными.
"""

import sqlite3
import logging
import random
import string
from datetime import datetime, date, timedelta

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_data.log")
    ]
)
logger = logging.getLogger("test_data")

# Путь к новой базе данных
DB_PATH = "full_api_new.db"

# Количество тестовых данных
NUM_ORGS = 10
NUM_DIVISIONS = 15
NUM_SECTIONS = 12
NUM_FUNCTIONS = 8
NUM_POSITIONS = 20
NUM_STAFF = 25

def get_db_connection():
    """Создает соединение с базой данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def random_string(length=6):
    """Генерирует случайную строку указанной длины"""
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

def random_date(start=date(2020, 1, 1), end=date.today()):
    """Генерирует случайную дату в указанном диапазоне"""
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def create_organizations():
    """Создает тестовые организации"""
    logger.info("Создание тестовых организаций...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Создаем холдинг
    cursor.execute(
        """
        INSERT INTO organizations (
            name, code, description, org_type, is_active
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            "OFS Global Holding",
            "OFS-HOLDING",
            "Головная компания OFS Global",
            "holding",
            1
        )
    )
    holding_id = cursor.lastrowid
    
    # Создаем юридические лица
    legal_entity_ids = []
    for i in range(4):
        cursor.execute(
            """
            INSERT INTO organizations (
                name, code, description, org_type, is_active, parent_id,
                inn, kpp, legal_address
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"ООО OFS-{random_string(3)}",
                f"OFS-LE-{i+1}",
                f"Юридическое лицо #{i+1}",
                "legal_entity",
                1,
                holding_id,
                f"77{random.randint(1000000, 9999999)}",
                f"77{random.randint(1000, 9999)}01",
                f"г. Москва, ул. Примерная, д. {random.randint(1, 100)}"
            )
        )
        legal_entity_ids.append(cursor.lastrowid)
    
    # Создаем локации
    location_ids = []
    for i in range(5):
        # Привязываем локацию к случайному юр.лицу
        parent_id = random.choice(legal_entity_ids)
        
        cursor.execute(
            """
            INSERT INTO organizations (
                name, code, description, org_type, is_active, parent_id,
                physical_address
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"Офис #{i+1}",
                f"OFS-LOC-{i+1}",
                f"Локация #{i+1}",
                "location",
                1,
                parent_id,
                f"г. {'Москва' if i < 3 else 'Санкт-Петербург'}, ул. {random.choice(['Центральная', 'Проспект Мира', 'Тверская', 'Невский'])}, д. {random.randint(1, 100)}"
            )
        )
        location_ids.append(cursor.lastrowid)
    
    conn.commit()
    conn.close()
    
    logger.info(f"Создано организаций: 1 холдинг, {len(legal_entity_ids)} юр.лиц, {len(location_ids)} локаций")
    return holding_id, legal_entity_ids, location_ids

def create_divisions(holding_id):
    """Создает тестовые подразделения"""
    logger.info("Создание тестовых подразделений...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    division_ids = []
    parent_divisions = []
    
    # Создаем корневые департаменты
    for i in range(5):
        cursor.execute(
            """
            INSERT INTO divisions (
                name, code, description, is_active, organization_id
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                f"Департамент {['ИТ', 'Финансов', 'Маркетинга', 'HR', 'Продаж'][i]}",
                f"DIV-{i+1}",
                f"Корневой департамент #{i+1}",
                1,
                holding_id
            )
        )
        div_id = cursor.lastrowid
        division_ids.append(div_id)
        parent_divisions.append(div_id)
    
    # Создаем подчиненные отделы
    for i in range(10):
        parent_id = random.choice(parent_divisions)
        cursor.execute(
            """
            INSERT INTO divisions (
                name, code, description, is_active, organization_id, parent_id
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                f"Отдел {random_string(4)}",
                f"DIV-SUB-{i+1}",
                f"Подчиненный отдел #{i+1}",
                1,
                holding_id,
                parent_id
            )
        )
        division_ids.append(cursor.lastrowid)
    
    conn.commit()
    conn.close()
    
    logger.info(f"Создано подразделений: {len(division_ids)}")
    return division_ids

def create_sections():
    """Создает тестовые секции"""
    logger.info("Создание тестовых секций...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    section_ids = []
    for i in range(NUM_SECTIONS):
        cursor.execute(
            """
            INSERT INTO sections (
                name, code, description, is_active
            ) VALUES (?, ?, ?, ?)
            """,
            (
                f"Секция {random_string(4)}",
                f"SEC-{i+1}",
                f"Тестовая секция #{i+1}",
                1
            )
        )
        section_ids.append(cursor.lastrowid)
    
    conn.commit()
    conn.close()
    
    logger.info(f"Создано секций: {len(section_ids)}")
    return section_ids

def create_functions():
    """Создает тестовые функции"""
    logger.info("Создание тестовых функций...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    functions = [
        "Разработка",
        "Тестирование",
        "Аналитика",
        "Управление проектами",
        "Дизайн",
        "Администрирование",
        "Поддержка",
        "Продажи"
    ]
    
    function_ids = []
    for i, func_name in enumerate(functions[:NUM_FUNCTIONS]):
        cursor.execute(
            """
            INSERT INTO functions (
                name, code, description, is_active
            ) VALUES (?, ?, ?, ?)
            """,
            (
                func_name,
                f"FUNC-{i+1}",
                f"Функция {func_name}",
                1
            )
        )
        function_ids.append(cursor.lastrowid)
    
    conn.commit()
    conn.close()
    
    logger.info(f"Создано функций: {len(function_ids)}")
    return function_ids

def create_positions(function_ids):
    """Создает тестовые должности"""
    logger.info("Создание тестовых должностей...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    position_names = [
        "Разработчик", "Старший разработчик", "Ведущий разработчик",
        "Тестировщик", "QA инженер", "Аналитик",
        "Системный аналитик", "Руководитель группы", "Менеджер проекта",
        "Дизайнер", "UI/UX дизайнер", "Администратор",
        "Специалист поддержки", "Менеджер по продажам", "Руководитель отдела",
        "Директор департамента", "Исполнительный директор", "Технический директор",
        "Финансовый директор", "Генеральный директор"
    ]
    
    position_ids = []
    for i, pos_name in enumerate(position_names[:NUM_POSITIONS]):
        # Привязываем должность к случайной функции или оставляем без функции
        function_id = random.choice(function_ids) if random.random() > 0.2 else None
        
        cursor.execute(
            """
            INSERT INTO positions (
                name, code, description, is_active, function_id
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                pos_name,
                f"POS-{i+1}",
                f"Должность {pos_name}",
                1,
                function_id
            )
        )
        position_ids.append(cursor.lastrowid)
    
    conn.commit()
    conn.close()
    
    logger.info(f"Создано должностей: {len(position_ids)}")
    return position_ids

def create_staff(legal_entity_ids, position_ids, division_ids, location_ids):
    """Создает тестовых сотрудников"""
    logger.info("Создание тестовых сотрудников...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    first_names = ["Иван", "Петр", "Алексей", "Сергей", "Дмитрий", "Михаил", "Андрей", "Николай", "Александр", "Владимир"]
    last_names = ["Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов", "Васильев", "Соколов", "Михайлов", "Новиков"]
    
    staff_ids = []
    used_emails = set()  # Для отслеживания уже использованных email адресов
    
    for i in range(NUM_STAFF):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Генерируем уникальный email с добавлением индекса и случайных символов
        email_base = f"{first_name.lower()}.{last_name.lower()}"
        email = f"{email_base}.{i+1}.{random_string(3).lower()}@example.com"
        
        # На всякий случай проверяем, что email уникальный
        while email in used_emails:
            email = f"{email_base}.{i+1}.{random_string(5).lower()}@example.com"
        
        used_emails.add(email)
        
        # Выбираем случайное юр.лицо
        organization_id = random.choice(legal_entity_ids)
        
        cursor.execute(
            """
            INSERT INTO staff (
                email, first_name, last_name, phone, description, is_active,
                organization_id, primary_organization_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                email,
                first_name,
                last_name,
                f"+7 9{random.randint(10, 99)} {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
                f"Тестовый сотрудник #{i+1}",
                1,
                organization_id,
                organization_id  # Используем то же значение для primary_organization_id
            )
        )
        staff_id = cursor.lastrowid
        staff_ids.append(staff_id)
        
        # Создаем связь с должностью
        position_id = random.choice(position_ids)
        division_id = random.choice(division_ids)
        location_id = random.choice(location_ids)
        
        cursor.execute(
            """
            INSERT INTO staff_positions (
                staff_id, position_id, division_id, location_id, is_primary, is_active,
                start_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                staff_id,
                position_id,
                division_id,
                location_id,
                1,
                1,
                random_date(date(2022, 1, 1)).isoformat()
            )
        )
        
        # Создаем связь с локацией
        cursor.execute(
            """
            INSERT INTO staff_locations (
                staff_id, location_id, is_current, date_from
            ) VALUES (?, ?, ?, ?)
            """,
            (
                staff_id,
                location_id,
                1,
                random_date(date(2022, 1, 1)).isoformat()
            )
        )
        
        # Для некоторых сотрудников создаем дополнительные должности
        if random.random() < 0.3:  # 30% шанс
            # Выбираем другую должность
            alt_position_id = random.choice([pos for pos in position_ids if pos != position_id])
            alt_division_id = random.choice(division_ids)
            
            cursor.execute(
                """
                INSERT INTO staff_positions (
                    staff_id, position_id, division_id, location_id, is_primary, is_active,
                    start_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    staff_id,
                    alt_position_id,
                    alt_division_id,
                    location_id,
                    0,  # не основная должность
                    1,
                    random_date(date(2022, 6, 1)).isoformat()
                )
            )
    
    conn.commit()
    conn.close()
    
    logger.info(f"Создано сотрудников: {len(staff_ids)}")
    return staff_ids

def create_functional_relations(staff_ids):
    """Создает тестовые функциональные отношения"""
    logger.info("Создание тестовых функциональных отношений...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    relation_types = ["functional", "administrative", "project", "territorial", "mentoring"]
    
    relation_count = 0
    # Выбираем несколько сотрудников как руководителей
    managers = random.sample(staff_ids, min(8, len(staff_ids) // 3))
    
    for manager_id in managers:
        # Каждому руководителю назначаем несколько подчиненных
        subordinates = random.sample([s for s in staff_ids if s != manager_id], random.randint(1, 5))
        
        for subordinate_id in subordinates:
            relation_type = random.choice(relation_types)
            
            cursor.execute(
                """
                INSERT INTO functional_relations (
                    manager_id, subordinate_id, relation_type, description, is_active,
                    start_date
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    manager_id,
                    subordinate_id,
                    relation_type,
                    f"{relation_type.capitalize()} подчинение",
                    1,
                    random_date(date(2022, 1, 1)).isoformat()
                )
            )
            relation_count += 1
    
    conn.commit()
    conn.close()
    
    logger.info(f"Создано функциональных отношений: {relation_count}")

def clear_database():
    """Очищает все таблицы перед заполнением новыми данными"""
    logger.info("Очистка базы данных...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Отключаем проверку внешних ключей на время удаления
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    # Получаем список всех таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
    tables = [row["name"] for row in cursor.fetchall()]
    
    # Удаляем данные из каждой таблицы
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            logger.info(f"Очищена таблица {table}")
        except Exception as e:
            logger.error(f"Ошибка при очистке таблицы {table}: {str(e)}")
    
    # Сбрасываем счетчики автоинкремента, только если таблица существует
    # cursor.execute("DELETE FROM sqlite_sequence")
    try:
        cursor.execute("DELETE FROM sqlite_sequence")
        logger.info("Сброшены счетчики автоинкремента (sqlite_sequence)")
    except sqlite3.OperationalError:
        logger.warning("Таблица sqlite_sequence не найдена или не может быть очищена")
    
    # Включаем проверку внешних ключей обратно
    cursor.execute("PRAGMA foreign_keys = ON")
    
    conn.commit()
    conn.close()
    
    logger.info("База данных успешно очищена")

def create_test_user():
    """Создает одного тестового пользователя, если его еще нет"""
    logger.info("Создание тестового пользователя...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже пользователь с таким email
    cursor.execute("SELECT id FROM user WHERE email = ?", ("test@example.com",))
    existing_user = cursor.fetchone()
    
    if not existing_user:
        try:
            # Импортируем хеширование пароля из full_api
            # (Предполагаем, что full_api.py в той же папке)
            from full_api import get_password_hash 
            
            hashed_password = get_password_hash("testpassword")
            
            cursor.execute(
                """
                INSERT INTO user (email, hashed_password, full_name, is_active, is_superuser) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "test@example.com",
                    hashed_password,
                    "Тестовый Пользователь",
                    1,
                    0
                )
            )
            conn.commit()
            logger.info("Тестовый пользователь test@example.com создан")
        except ImportError:
            logger.error("Не удалось импортировать get_password_hash из full_api.py")
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Ошибка SQLite при создании тестового пользователя: {str(e)}")
        except Exception as e:
            conn.rollback()
            logger.error(f"Неизвестная ошибка при создании тестового пользователя: {str(e)}")
    else:
        logger.info("Тестовый пользователь test@example.com уже существует")
        
    conn.close()

def main():
    """Основная функция для заполнения базы данных тестовыми данными"""
    logger.info("Начало заполнения базы данных тестовыми данными...")
    
    # !!! ВАЖНО: Добавляем подтверждение перед очисткой !!!
    confirmation = input("ПРЕДУПРЕЖДЕНИЕ: Этот скрипт УДАЛИТ все данные из таблиц (кроме user) и заполнит их ТЕСТОВЫМИ данными.\nТы уверен, что хочешь продолжить? Введи 'YES' для подтверждения: ")
    if confirmation.strip().upper() != 'YES':
        logger.warning("Операция отменена пользователем.")
        print("Операция отменена.")
        return # Выходим из функции, если нет подтверждения
    
    logger.info("Подтверждение получено, продолжаем...")
    
    # Очищаем базу данных перед заполнением (КРОМЕ user!)
    clear_database()
    
    # Шаг 0: Убедимся, что тестовый пользователь существует
    create_test_user()
    
    # Шаг 1: Создаем организации
    holding_id, legal_entity_ids, location_ids = create_organizations()
    
    # Шаг 2: Создаем подразделения
    division_ids = create_divisions(holding_id)
    
    # Шаг 3: Создаем секции
    section_ids = create_sections()
    
    # Шаг 4: Создаем функции
    function_ids = create_functions()
    
    # Шаг 5: Создаем должности
    position_ids = create_positions(function_ids)
    
    # Шаг 6: Создаем сотрудников
    staff_ids = create_staff(legal_entity_ids, position_ids, division_ids, location_ids)
    
    # Шаг 7: Создаем функциональные отношения
    create_functional_relations(staff_ids)
    
    logger.info("Заполнение базы данных тестовыми данными успешно завершено!")

if __name__ == "__main__":
    main() 