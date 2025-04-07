#!/usr/bin/env python
"""
НОВЫЙ СКРИПТ!
Удаляет старую базу данных, инициализирует её с актуальной схемой из full_api.py 
и заполняет тестовыми данными.
ЗАПУСКАТЬ ТОЛЬКО ЭТОТ СКРИПТ!
"""

import sqlite3
import logging
import random
import string
from datetime import datetime, date, timedelta
import json
import os
import sys

# Добавляем путь к корневой папке, чтобы импортировать full_api
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("reset_and_fill.log")
    ]
)
logger = logging.getLogger("reset_fill_data")

# Путь к базе данных
DB_PATH = "full_api_new.db"

# --- ВАЖНО: Импорт функции инициализации БД из основного API ---
try:
    # Попытка импортировать функцию init_db
    from full_api import init_db as initialize_database_schema
    logger.info("Функция init_db() успешно импортирована из full_api.py")
except ImportError as e:
    logger.error(f"Не удалось импортировать init_db из full_api: {e}")
    logger.error("Убедитесь, что скрипт запускается из папки backend или что full_api.py доступен.")
    # Можно либо остановить скрипт, либо определить init_db прямо здесь, скопировав код
    # Определим ее здесь как запасной вариант, скопировав логику создания таблиц
    logger.warning("Используется запасная реализация init_db() внутри скрипта.")
    def initialize_database_schema():
        logger.info("Выполняется ЗАПАСНАЯ инициализация базы данных...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Вставьте сюда ТОЧНЫЕ КОМАНДЫ CREATE TABLE из вашей функции init_db в full_api.py
        # Пример (!!! ЗАМЕНИТЕ НА ВАШ АКТУАЛЬНЫЙ КОД СОЗДАНИЯ ТАБЛИЦ !!!):
        # Таблица Пользователи (user) - ВАЖНО: добавлена created_at
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            is_superuser BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        # Таблица Организации (organizations)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            description TEXT,
            org_type TEXT CHECK(org_type IN ('board', 'holding', 'legal_entity', 'location')) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            parent_id INTEGER,
            ckp TEXT,
            inn TEXT,
            kpp TEXT,
            legal_address TEXT,
            physical_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES organizations (id) ON DELETE SET NULL
        )
        """)
        # Таблица Подразделения (divisions)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS divisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            organization_id INTEGER NOT NULL,
            parent_id INTEGER,
            ckp TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations (id) ON DELETE CASCADE,
            FOREIGN KEY (parent_id) REFERENCES divisions (id) ON DELETE SET NULL
        )
        """)
        # Таблица Отделы (sections) - пока опционально
        # cursor.execute(""" CREATE TABLE IF NOT EXISTS sections (...) """)
        # Таблица Функции (functions)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS functions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        # Таблица Должности (positions)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            function_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (function_id) REFERENCES functions (id) ON DELETE SET NULL
        )
        """)
        # Таблица Сотрудники (staff) - с новыми полями
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            middle_name TEXT,
            phone TEXT,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            organization_id INTEGER,
            primary_organization_id INTEGER,
            location_id INTEGER,
            photo_path TEXT, -- Путь к фото
            document_paths TEXT, -- JSON строка со списком путей к документам
            telegram_id TEXT,
            vk TEXT,
            instagram TEXT,
            registration_address TEXT,
            actual_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations (id) ON DELETE SET NULL,
            FOREIGN KEY (primary_organization_id) REFERENCES organizations (id) ON DELETE SET NULL,
            FOREIGN KEY (location_id) REFERENCES organizations (id) ON DELETE SET NULL
        )
        """)
        # Таблица Связь Сотрудник-Должность (staff_positions)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            position_id INTEGER NOT NULL,
            division_id INTEGER, -- Может быть не привязан к подразделению напрямую
            location_id INTEGER, -- Должность может быть в конкретной локации
            is_primary BOOLEAN DEFAULT TRUE, -- Основная ли это должность
            is_active BOOLEAN DEFAULT TRUE, -- Актуальна ли связь
            start_date DATE NOT NULL,
            end_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (staff_id) REFERENCES staff (id) ON DELETE CASCADE,
            FOREIGN KEY (position_id) REFERENCES positions (id) ON DELETE CASCADE,
            FOREIGN KEY (division_id) REFERENCES divisions (id) ON DELETE SET NULL,
            FOREIGN KEY (location_id) REFERENCES organizations (id) ON DELETE SET NULL
        )
        """)
        # Таблица Функциональные связи (functional_relations) - если нужна
        # cursor.execute(""" CREATE TABLE IF NOT EXISTS functional_relations (...) """)
        # ... добавьте здесь создание ВСЕХ ваших таблиц ...

        conn.commit()
        conn.close()
        logger.info("ЗАПАСНАЯ инициализация базы данных завершена.")
# --- КОНЕЦ ИМПОРТА И ЗАПАСНОЙ РЕАЛИЗАЦИИ ---

# Количество тестовых данных (можно настроить)
NUM_ORGS_LEGAL = 4
NUM_ORGS_LOCATION = 5
NUM_DIVISIONS_ROOT = 5
NUM_DIVISIONS_SUB = 10
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

# --- Функции создания данных (копируем из старого скрипта) ---

def create_organizations():
    """Создает тестовые организации"""
    logger.info("Создание тестовых организаций...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM organizations") # Чистим таблицу перед заполнением
    conn.commit()

    # Создаем холдинг
    cursor.execute(
        "INSERT INTO organizations (name, code, description, org_type, is_active) VALUES (?, ?, ?, ?, ?)",
        ("OFS Global Holding", "OFS-HOLDING", "Головная компания OFS Global", "holding", 1)
    )
    holding_id = cursor.lastrowid

    # Создаем юридические лица
    legal_entity_ids = []
    for i in range(NUM_ORGS_LEGAL):
        cursor.execute(
            "INSERT INTO organizations (name, code, description, org_type, is_active, parent_id, inn, kpp, legal_address) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (f"ООО OFS-{random_string(3)}", f"OFS-LE-{i+1}", f"Юридическое лицо #{i+1}", "legal_entity", 1, holding_id, f"77{random.randint(1000000, 9999999)}", f"77{random.randint(1000, 9999)}01", f"г. Москва, ул. Примерная, д. {random.randint(1, 100)}")
        )
        legal_entity_ids.append(cursor.lastrowid)

    # Создаем локации
    location_ids = []
    for i in range(NUM_ORGS_LOCATION):
        parent_id = random.choice(legal_entity_ids)
        cursor.execute(
            "INSERT INTO organizations (name, code, description, org_type, is_active, parent_id, physical_address) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (f"Офис #{i+1}", f"OFS-LOC-{i+1}", f"Локация #{i+1}", "location", 1, parent_id, f"г. {'Москва' if i < 3 else 'Санкт-Петербург'}, ул. {random.choice(['Центральная', 'Проспект Мира', 'Тверская', 'Невский'])}, д. {random.randint(1, 100)}")
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
    cursor.execute("DELETE FROM divisions")
    conn.commit()

    division_ids = []
    parent_divisions = []

    for i in range(NUM_DIVISIONS_ROOT):
        cursor.execute(
            "INSERT INTO divisions (name, code, description, is_active, organization_id) VALUES (?, ?, ?, ?, ?)",
            (f"Департамент {['ИТ', 'Финансов', 'Маркетинга', 'HR', 'Продаж'][i % 5]}", f"DIV-{i+1}", f"Корневой департамент #{i+1}", 1, holding_id)
        )
        div_id = cursor.lastrowid
        division_ids.append(div_id)
        parent_divisions.append(div_id)

    for i in range(NUM_DIVISIONS_SUB):
        parent_id = random.choice(parent_divisions)
        cursor.execute(
            "INSERT INTO divisions (name, code, description, is_active, organization_id, parent_id) VALUES (?, ?, ?, ?, ?, ?)",
            (f"Отдел {random_string(4)}", f"DIV-SUB-{i+1}", f"Подчиненный отдел #{i+1}", 1, holding_id, parent_id)
        )
        division_ids.append(cursor.lastrowid)

    conn.commit()
    conn.close()
    logger.info(f"Создано подразделений: {len(division_ids)}")
    return division_ids

def create_functions():
    """Создает тестовые функции"""
    logger.info("Создание тестовых функций...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM functions")
    conn.commit()

    functions = ["Разработка", "Тестирование", "Аналитика", "Управление проектами", "Дизайн", "Администрирование", "Поддержка", "Продажи"]
    function_ids = []
    for i, func_name in enumerate(functions[:NUM_FUNCTIONS]):
        cursor.execute(
            "INSERT INTO functions (name, code, description, is_active) VALUES (?, ?, ?, ?)",
            (func_name, f"FUNC-{i+1}", f"Функция {func_name}", 1)
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
    cursor.execute("DELETE FROM positions")
    cursor.execute("DELETE FROM staff_positions") # Чистим и связи
    conn.commit()

    positions = ["Разработчик", "Тестировщик", "Аналитик", "Менеджер проектов", "Дизайнер", "Администратор", "Специалист поддержки", "Менеджер по продажам", "Руководитель отдела", "Директор департамента"]
    position_ids = []
    for i in range(NUM_POSITIONS):
        pos_name = random.choice(positions) + f" {random.choice(['младший','','старший','ведущий'])}"
        func_id = random.choice(function_ids + [None])
        cursor.execute(
            "INSERT INTO positions (name, code, description, is_active, function_id) VALUES (?, ?, ?, ?, ?)",
            (pos_name, f"POS-{i+1}", f"Должность {pos_name}", 1, func_id)
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
    cursor.execute("DELETE FROM staff")
    cursor.execute("DELETE FROM staff_positions") # Чистим и связи
    conn.commit()

    first_names = ["Иван", "Петр", "Сергей", "Анна", "Мария", "Елена", "Дмитрий", "Алексей"]
    last_names = ["Иванов", "Петров", "Сидоров", "Смирнова", "Кузнецова", "Попова", "Васильев", "Михайлов"]
    middle_names = ["Иванович", "Петрович", "Сергеевич", "Дмитриевна", "Алексеевна", "Владимировна", None]

    staff_ids = []
    for i in range(NUM_STAFF):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        middle_name = random.choice(middle_names)
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1,99)}@ofs.test"
        phone = f"+7 9{random.randint(10, 99)} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
        is_active = random.choice([True, True, True, False])
        organization_id = random.choice(legal_entity_ids) # Привязка к юр. лицу
        primary_organization_id = organization_id # Пока считаем, что основное место = юр. лицо
        location_id = random.choice(location_ids) # Случайная локация
        telegram_id = f"@{first_name.lower()}_{last_name.lower()}{random.randint(1,10)}"
        vk = f"https://vk.com/id{random.randint(10000, 99999)}"
        instagram = f"@{first_name.lower()}{last_name.lower()}"
        registration_address = f"г. Москва, ул. Регистрации, д. {random.randint(1, 50)}, кв. {random.randint(1, 200)}"
        actual_address = random.choice([registration_address, f"г. Москва, ул. Фактическая, д. {random.randint(1, 100)}"])
        description = f"Тестовый сотрудник {i+1}. {random.choice(['Ответственный', 'Исполнительный', 'Креативный', ''])}."

        # --- ФЕЙКОВЫЕ ДАННЫЕ ДЛЯ ФАЙЛОВ ---
        photo_path = random.choice([None, f"backend/uploads/staff/placeholder_avatar_{random.randint(1,3)}.png"]) # Фейковый путь
        num_docs = random.randint(0, 3)
        document_paths = []
        if num_docs > 0:
            for j in range(num_docs):
                document_paths.append(f"backend/uploads/staff/placeholder_doc_{random.randint(1,5)}.pdf") # Фейковые пути
        document_paths_json = json.dumps(document_paths)
        # --- КОНЕЦ ФЕЙКОВЫХ ДАННЫХ ---

        # Вставляем сотрудника со всеми новыми полями
        try:
            cursor.execute(
                """
                INSERT INTO staff (
                    email, first_name, last_name, middle_name,
                    phone, description, is_active, organization_id,
                    primary_organization_id, location_id,
                    registration_address, actual_address,
                    telegram_id, vk, instagram,
                    photo_path, document_paths
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    email,
                    first_name,
                    last_name,
                    middle_name,
                    phone,
                    description,
                    1 if is_active else 0,
                    organization_id,
                    primary_organization_id,
                    location_id,
                    registration_address,
                    actual_address,
                    telegram_id,
                    vk,
                    instagram,
                    photo_path, # Вставляем путь к фото
                    document_paths_json # Вставляем JSON с путями к документам
                )
            )
            staff_id = cursor.lastrowid
            staff_ids.append(staff_id)

            # Добавляем хотя бы одну связь с должностью для каждого сотрудника
            position_id = random.choice(position_ids)
            division_id = random.choice(division_ids + [None]) # Может быть без подразделения
            pos_location_id = random.choice(location_ids + [None]) # Должность может быть в другой локации
            is_primary_pos = True
            start_date_pos = random_date(end=date.today() - timedelta(days=30))
            end_date_pos = random.choice([None, random_date(start=start_date_pos + timedelta(days=100))])

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
                     pos_location_id,
                     1 if is_primary_pos else 0,
                     1 if end_date_pos is None else 0, # Активна, если нет даты окончания
                     start_date_pos.isoformat(),
                     end_date_pos.isoformat() if end_date_pos else None
                 )
            )

        except sqlite3.IntegrityError as e:
            logger.warning(f"Ошибка при создании сотрудника {email} или его должности: {str(e)}")
            conn.rollback()
            continue

    conn.commit()
    conn.close()
    logger.info(f"Создано сотрудников: {len(staff_ids)}")
    return staff_ids

# --- Основная функция --- 
def main():
    logger.info("=== ЗАПУСК СКРИПТА ПЕРЕСОЗДАНИЯ И ЗАПОЛНЕНИЯ БАЗЫ ДАННЫХ ===")
    
    # Шаг 1: Удаляем старую БД
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            logger.info(f"Старый файл базы данных '{DB_PATH}' удален.")
        except OSError as e:
            logger.error(f"Не удалось удалить старый файл базы данных '{DB_PATH}': {e}")
            return # Прерываем выполнение, если не можем удалить старую БД
    else:
        logger.info(f"Файл базы данных '{DB_PATH}' не найден, удаление не требуется.")
        
    # Шаг 2: Инициализируем БД с актуальной схемой
    try:
        logger.info(f"Инициализация новой базы данных '{DB_PATH}' с использованием схемы из full_api.py...")
        initialize_database_schema() # Вызываем импортированную или запасную функцию
        logger.info("Инициализация схемы базы данных завершена успешно.")
    except Exception as e:
        logger.error(f"Критическая ошибка при инициализации схемы базы данных: {e}")
        return # Прерываем выполнение
        
    # Шаг 3: Создаем тестовые данные
    logger.info("Начинаем создание тестовых данных...")
    try:
        holding_id, legal_entity_ids, location_ids = create_organizations()
        division_ids = create_divisions(holding_id)
        function_ids = create_functions()
        position_ids = create_positions(function_ids)
        create_staff(legal_entity_ids, position_ids, division_ids, location_ids)
        # Добавьте здесь вызовы для создания связей, если нужно
        # create_division_sections(division_ids, section_ids) # Пример
        # create_section_functions(section_ids, function_ids) # Пример
        logger.info("Создание тестовых данных успешно завершено.")
    except Exception as e:
        logger.error(f"Ошибка при создании тестовых данных: {e}", exc_info=True)
        logger.error("База данных может быть создана, но заполнена не полностью.")

    logger.info("=== ЗАВЕРШЕНИЕ РАБОТЫ СКРИПТА ===")

if __name__ == "__main__":
    main() 