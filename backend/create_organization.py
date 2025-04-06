import sqlite3
import logging
import sys
import os
from datetime import datetime, timedelta
import random

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("org_creation")

DB_PATH = "full_api_new.db"

def get_db_connection():
    """Создает подключение к базе данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def random_string(length=5):
    """Генерирует случайную строку из букв"""
    import string
    letters = string.ascii_uppercase
    return ''.join(random.choice(letters) for _ in range(length))

def create_holding():
    """Создает холдинг в таблице organizations"""
    logger.info("Создание холдинга...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверим, существует ли холдинг
    cursor.execute("SELECT id FROM organizations WHERE org_type = 'holding'")
    existing = cursor.fetchone()
    
    if existing:
        logger.info(f"Холдинг уже существует с ID: {existing['id']}")
        holding_id = existing['id']
    else:
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
        logger.info(f"Создан холдинг с ID: {holding_id}")
    
    conn.commit()
    return holding_id

def create_legal_entities(holding_id):
    """Создает юридические лица в таблице organizations"""
    logger.info("Создание юридических лиц...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверим существующие юр.лица
    cursor.execute("SELECT id FROM organizations WHERE org_type = 'legal_entity' AND parent_id = ?", (holding_id,))
    existing = cursor.fetchall()
    
    if existing:
        logger.info(f"Уже существует {len(existing)} юридических лиц")
        legal_entity_ids = [row["id"] for row in existing]
    else:
        legal_entity_ids = []
        
        # Создаем 3 юридических лица
        for i in range(3):
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
            legal_entity_id = cursor.lastrowid
            legal_entity_ids.append(legal_entity_id)
            logger.info(f"Создано юридическое лицо с ID: {legal_entity_id}")
    
    conn.commit()
    return legal_entity_ids

def create_locations(legal_entity_ids):
    """Создает локации (офисы) в таблице organizations"""
    logger.info("Создание локаций (офисов)...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверим существующие локации
    existing_locations = {}
    for legal_id in legal_entity_ids:
        cursor.execute("SELECT id FROM organizations WHERE org_type = 'location' AND parent_id = ?", (legal_id,))
        existing = cursor.fetchall()
        if existing:
            existing_locations[legal_id] = [row["id"] for row in existing]
    
    if any(existing_locations.values()):
        logger.info(f"Уже существуют локации для {len(existing_locations)} юридических лиц")
        location_ids = []
        for locations in existing_locations.values():
            location_ids.extend(locations)
    else:
        location_ids = []
        cities = ["Москва", "Санкт-Петербург", "Казань", "Екатеринбург", "Новосибирск"]
        
        # Создаем по 1-2 локации для каждого юр.лица
        for legal_id in legal_entity_ids:
            num_locations = random.randint(1, 2)
            for i in range(num_locations):
                city = random.choice(cities)
                cursor.execute(
                    """
                    INSERT INTO organizations (
                        name, code, description, org_type, is_active, parent_id,
                        physical_address
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        f"Офис {city}",
                        f"OFS-LOC-{legal_id}-{i+1}",
                        f"Офис в городе {city}",
                        "location",
                        1,
                        legal_id,
                        f"г. {city}, ул. {random_string(8)}, д. {random.randint(1, 100)}"
                    )
                )
                location_id = cursor.lastrowid
                location_ids.append(location_id)
                logger.info(f"Создана локация с ID: {location_id} (для юр.лица {legal_id})")
    
    conn.commit()
    return location_ids

def create_divisions(legal_entity_ids):
    """Создает департаменты в таблице divisions"""
    logger.info("Создание департаментов...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверим существующие департаменты
    cursor.execute("SELECT id FROM divisions")
    existing = cursor.fetchall()
    
    if existing:
        logger.info(f"Уже существует {len(existing)} департаментов")
        division_ids = [row["id"] for row in existing]
    else:
        # Список департаментов для создания
        departments = [
            {
                "name": "Финансовый департамент",
                "code": "FINANCE",
                "description": "Управление финансами компании"
            },
            {
                "name": "Коммерческий департамент",
                "code": "COMMERCE",
                "description": "Продажи и развитие бизнеса"
            },
            {
                "name": "ИТ-департамент",
                "code": "IT",
                "description": "Информационные технологии"
            },
            {
                "name": "HR-департамент",
                "code": "HR",
                "description": "Управление персоналом"
            },
            {
                "name": "Департамент маркетинга",
                "code": "MARKETING",
                "description": "Маркетинг и продвижение"
            }
        ]
        
        division_ids = []
        
        # Распределяем департаменты между юр.лицами
        for i, dept in enumerate(departments):
            legal_id = legal_entity_ids[i % len(legal_entity_ids)]
            cursor.execute(
                """
                INSERT INTO divisions (
                    name, code, description, is_active, organization_id
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    dept["name"],
                    dept["code"],
                    dept["description"],
                    1,
                    legal_id
                )
            )
            division_id = cursor.lastrowid
            division_ids.append(division_id)
            logger.info(f"Создан департамент {dept['name']} с ID: {division_id} (в юр.лице {legal_id})")
    
    conn.commit()
    return division_ids

def create_sections():
    """Создает отделы в таблице sections"""
    logger.info("Создание отделов...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверим существующие отделы
    cursor.execute("SELECT id FROM sections")
    existing = cursor.fetchall()
    
    if existing:
        logger.info(f"Уже существует {len(existing)} отделов")
        section_ids = [row["id"] for row in existing]
    else:
        # Список отделов для создания
        sections = [
            # Финансовые отделы
            {
                "name": "Отдел бухгалтерии",
                "code": "ACCOUNTING",
                "description": "Бухгалтерский учет и отчетность",
                "department_code": "FINANCE"
            },
            {
                "name": "Отдел казначейства",
                "code": "TREASURY",
                "description": "Управление денежными потоками",
                "department_code": "FINANCE"
            },
            # Коммерческие отделы
            {
                "name": "Отдел продаж",
                "code": "SALES",
                "description": "Продажи продуктов и услуг",
                "department_code": "COMMERCE"
            },
            {
                "name": "Отдел по работе с клиентами",
                "code": "CUSTOMER",
                "description": "Клиентская поддержка",
                "department_code": "COMMERCE"
            },
            # ИТ отделы
            {
                "name": "Отдел разработки",
                "code": "DEV",
                "description": "Разработка ПО",
                "department_code": "IT"
            },
            {
                "name": "Отдел тестирования",
                "code": "QA",
                "description": "Обеспечение качества",
                "department_code": "IT"
            },
            {
                "name": "Отдел инфраструктуры",
                "code": "INFRA",
                "description": "ИТ-инфраструктура",
                "department_code": "IT"
            },
            # HR отделы
            {
                "name": "Отдел подбора персонала",
                "code": "RECRUITING",
                "description": "Поиск и найм сотрудников",
                "department_code": "HR"
            },
            {
                "name": "Отдел оценки и развития",
                "code": "DEVELOPMENT",
                "description": "Оценка и развитие сотрудников",
                "department_code": "HR"
            },
            # Маркетинг отделы
            {
                "name": "Отдел рекламы",
                "code": "ADVERTISING",
                "description": "Реклама и маркетинговые коммуникации",
                "department_code": "MARKETING"
            },
            {
                "name": "Отдел аналитики",
                "code": "ANALYTICS",
                "description": "Маркетинговая аналитика",
                "department_code": "MARKETING"
            }
        ]
        
        # Сначала получим ID департаментов
        dept_ids = {}
        cursor.execute("SELECT id, code FROM divisions")
        for row in cursor.fetchall():
            dept_ids[row["code"]] = row["id"]
        
        section_ids = []
        division_sections = []
        
        # Создаем отделы
        for section in sections:
            cursor.execute(
                """
                INSERT INTO sections (
                    name, code, description, is_active
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    section["name"],
                    section["code"],
                    section["description"],
                    1
                )
            )
            section_id = cursor.lastrowid
            section_ids.append(section_id)
            
            # Запомним связь с департаментом
            if section["department_code"] in dept_ids:
                division_sections.append({
                    "section_id": section_id,
                    "division_id": dept_ids[section["department_code"]]
                })
            
            logger.info(f"Создан отдел {section['name']} с ID: {section_id}")
        
        # Создаем связи между отделами и департаментами
        for link in division_sections:
            cursor.execute(
                """
                INSERT INTO division_sections (
                    division_id, section_id, is_primary
                ) VALUES (?, ?, ?)
                """,
                (
                    link["division_id"],
                    link["section_id"],
                    1  # primary
                )
            )
            logger.info(f"Связан отдел {link['section_id']} с департаментом {link['division_id']}")
    
    conn.commit()
    return section_ids

def create_functions():
    """Создает функции в таблице functions и связывает их с отделами"""
    logger.info("Создание функций...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверим существующие функции
    cursor.execute("SELECT id FROM functions")
    existing = cursor.fetchall()
    
    if existing:
        logger.info(f"Уже существует {len(existing)} функций")
        function_ids = [row["id"] for row in existing]
    else:
        # Список функций для создания
        functions = [
            # Финансовые функции
            {
                "name": "Управление финансами",
                "code": "FINANCE_MGMT",
                "description": "Финансовое планирование и управление",
                "section_code": "ACCOUNTING"
            },
            {
                "name": "Бухгалтерский учет",
                "code": "ACCOUNTING",
                "description": "Ведение бухгалтерского учета",
                "section_code": "ACCOUNTING"
            },
            # Коммерческие функции
            {
                "name": "Продажи",
                "code": "SALES",
                "description": "Продажи продуктов и услуг",
                "section_code": "SALES"
            },
            {
                "name": "Работа с клиентами",
                "code": "CUSTOMER_SERVICE",
                "description": "Обслуживание клиентов",
                "section_code": "CUSTOMER"
            },
            # ИТ функции
            {
                "name": "Разработка ПО",
                "code": "SOFTWARE_DEV",
                "description": "Разработка программного обеспечения",
                "section_code": "DEV"
            },
            {
                "name": "Тестирование",
                "code": "TESTING",
                "description": "Тестирование ПО",
                "section_code": "QA"
            },
            {
                "name": "Системное администрирование",
                "code": "SYSADMIN",
                "description": "Администрирование систем",
                "section_code": "INFRA"
            },
            # HR функции
            {
                "name": "Рекрутмент",
                "code": "RECRUITMENT",
                "description": "Подбор персонала",
                "section_code": "RECRUITING"
            },
            {
                "name": "Развитие персонала",
                "code": "PERSONNEL_DEV",
                "description": "Обучение и развитие персонала",
                "section_code": "DEVELOPMENT"
            },
            # Маркетинг функции
            {
                "name": "Маркетинговые коммуникации",
                "code": "MARKETING_COMM",
                "description": "Коммуникационные кампании",
                "section_code": "ADVERTISING"
            },
            {
                "name": "Маркетинговый анализ",
                "code": "MARKETING_ANALYTICS",
                "description": "Анализ рынка и маркетинговых данных",
                "section_code": "ANALYTICS"
            }
        ]
        
        # Сначала получим ID отделов
        section_ids = {}
        cursor.execute("SELECT id, code FROM sections")
        for row in cursor.fetchall():
            section_ids[row["code"]] = row["id"]
        
        function_ids = []
        section_functions = []
        
        # Создаем функции
        for function in functions:
            cursor.execute(
                """
                INSERT INTO functions (
                    name, code, description, is_active
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    function["name"],
                    function["code"],
                    function["description"],
                    1
                )
            )
            function_id = cursor.lastrowid
            function_ids.append(function_id)
            
            # Запомним связь с отделом
            if function["section_code"] in section_ids:
                section_functions.append({
                    "function_id": function_id,
                    "section_id": section_ids[function["section_code"]]
                })
            
            logger.info(f"Создана функция {function['name']} с ID: {function_id}")
        
        # Создаем связи между функциями и отделами
        for link in section_functions:
            cursor.execute(
                """
                INSERT INTO section_functions (
                    section_id, function_id, is_primary
                ) VALUES (?, ?, ?)
                """,
                (
                    link["section_id"],
                    link["function_id"],
                    1  # primary
                )
            )
            logger.info(f"Связана функция {link['function_id']} с отделом {link['section_id']}")
    
    conn.commit()
    return function_ids

def create_positions(function_ids):
    """Создает должности в таблице positions"""
    logger.info("Создание должностей...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получим ID функций
    function_dict = {}
    cursor.execute("SELECT id, code FROM functions")
    for row in cursor.fetchall():
        function_dict[row["code"]] = row["id"]
    
    # Список должностей для создания
    positions = [
        # Финансовые должности
        {
            "name": "Главный бухгалтер",
            "code": "CHIEF_ACCOUNTANT",
            "description": "Руководитель бухгалтерии",
            "function_code": "ACCOUNTING"
        },
        {
            "name": "Бухгалтер",
            "code": "ACCOUNTANT",
            "description": "Ведение бухгалтерского учета",
            "function_code": "ACCOUNTING"
        },
        # Коммерческие должности
        {
            "name": "Руководитель отдела продаж",
            "code": "SALES_MANAGER",
            "description": "Управление продажами",
            "function_code": "SALES"
        },
        {
            "name": "Менеджер по продажам",
            "code": "SALES_SPECIALIST",
            "description": "Продажи продуктов и услуг",
            "function_code": "SALES"
        },
        # ИТ должности
        {
            "name": "Руководитель разработки",
            "code": "DEV_LEAD",
            "description": "Руководитель команды разработки",
            "function_code": "SOFTWARE_DEV"
        },
        {
            "name": "Разработчик",
            "code": "DEVELOPER",
            "description": "Разработка ПО",
            "function_code": "SOFTWARE_DEV"
        },
        {
            "name": "Руководитель QA",
            "code": "QA_LEAD",
            "description": "Руководитель команды тестирования",
            "function_code": "TESTING"
        },
        {
            "name": "Тестировщик",
            "code": "QA_ENGINEER",
            "description": "Тестирование ПО",
            "function_code": "TESTING"
        },
        {
            "name": "Системный администратор",
            "code": "SYSADMIN",
            "description": "Администрирование систем",
            "function_code": "SYSADMIN"
        },
        # HR должности
        {
            "name": "Рекрутер",
            "code": "RECRUITER",
            "description": "Поиск и найм персонала",
            "function_code": "RECRUITMENT"
        },
        {
            "name": "Специалист по обучению",
            "code": "TRAINER",
            "description": "Обучение сотрудников",
            "function_code": "PERSONNEL_DEV"
        },
        # Маркетинг должности
        {
            "name": "Маркетолог",
            "code": "MARKETER",
            "description": "Разработка и реализация маркетинговых кампаний",
            "function_code": "MARKETING_COMM"
        },
        {
            "name": "Аналитик",
            "code": "ANALYST",
            "description": "Анализ данных",
            "function_code": "MARKETING_ANALYTICS"
        }
    ]
    
    # Проверим существующие должности
    existing_positions = {}
    cursor.execute("SELECT id, code FROM positions WHERE code NOT IN ('BOARD-MEMBER', 'CEO', 'CFO', 'CCO', 'CTO', 'HEAD-DEP', 'HEAD-SEC')")
    for row in cursor.fetchall():
        existing_positions[row["code"]] = row["id"]
    
    if existing_positions:
        logger.info(f"Уже существует {len(existing_positions)} обычных должностей")
        position_ids = list(existing_positions.values())
    else:
        position_ids = []
        
        # Создаем должности
        for position in positions:
            function_id = function_dict.get(position["function_code"])
            
            cursor.execute(
                """
                INSERT INTO positions (
                    name, code, description, is_active, function_id
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    position["name"],
                    position["code"],
                    position["description"],
                    1,
                    function_id
                )
            )
            position_id = cursor.lastrowid
            position_ids.append(position_id)
            logger.info(f"Создана должность {position['name']} с ID: {position_id}")
    
    conn.commit()
    return position_ids

def main():
    try:
        holding_id = create_holding()
        legal_entity_ids = create_legal_entities(holding_id)
        location_ids = create_locations(legal_entity_ids)
        division_ids = create_divisions(legal_entity_ids)
        section_ids = create_sections()
        function_ids = create_functions()
        position_ids = create_positions(function_ids)
        
        logger.info(f"Создание организационной структуры успешно завершено!")
        logger.info(f"Холдинг: ID={holding_id}")
        logger.info(f"Юридические лица: {len(legal_entity_ids)} записей")
        logger.info(f"Локации: {len(location_ids)} записей")
        logger.info(f"Департаменты: {len(division_ids)} записей")
        logger.info(f"Отделы: {len(section_ids)} записей")
        logger.info(f"Функции: {len(function_ids)} записей")
        logger.info(f"Должности: {len(position_ids)} записей")
    except Exception as e:
        logger.error(f"Ошибка при создании организационной структуры: {e}")
        raise

if __name__ == "__main__":
    main() 