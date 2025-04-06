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
logger = logging.getLogger("board_creation")

DB_PATH = "full_api_new.db"

def get_db_connection():
    """Создает подключение к базе данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_board():
    """Создает запись Совета учредителей в таблице organizations"""
    logger.info("Создание записи Совета учредителей...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверим, существует ли уже запись с типом "board"
    cursor.execute("SELECT id FROM organizations WHERE org_type = 'board'")
    existing = cursor.fetchone()
    
    if existing:
        logger.info(f"Запись Совета учредителей уже существует с ID: {existing['id']}")
        board_id = existing['id']
    else:
        # Создаем запись Совета учредителей
        cursor.execute(
            """
            INSERT INTO organizations (
                name, code, description, org_type, is_active
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                "Совет учредителей OFS Global",
                "OFS-BOARD",
                "Высший орган управления OFS Global",
                "board",
                1
            )
        )
        board_id = cursor.lastrowid
        logger.info(f"Создана запись Совета учредителей с ID: {board_id}")
    
    conn.commit()
    return board_id

def create_executive_positions():
    """Создает должности высшего руководства"""
    logger.info("Создание должностей высшего руководства...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Список должностей для создания
    positions = [
        {
            "name": "Член совета учредителей",
            "code": "BOARD-MEMBER",
            "description": "Участник высшего органа управления"
        },
        {
            "name": "Генеральный директор",
            "code": "CEO",
            "description": "Главное должностное лицо компании"
        },
        {
            "name": "Финансовый директор",
            "code": "CFO",
            "description": "Руководитель финансового направления"
        },
        {
            "name": "Коммерческий директор",
            "code": "CCO",
            "description": "Руководитель коммерческого направления"
        },
        {
            "name": "Технический директор",
            "code": "CTO",
            "description": "Руководитель технического направления"
        },
        {
            "name": "Руководитель департамента",
            "code": "HEAD-DEP",
            "description": "Руководитель функционального подразделения"
        },
        {
            "name": "Руководитель отдела",
            "code": "HEAD-SEC",
            "description": "Руководитель структурного подразделения"
        }
    ]
    
    # Проверим существующие должности и создадим новые, если их нет
    position_ids = {}
    
    for position in positions:
        # Проверяем существование
        cursor.execute("SELECT id FROM positions WHERE code = ?", (position["code"],))
        existing = cursor.fetchone()
        
        if existing:
            logger.info(f"Должность {position['name']} уже существует с ID: {existing['id']}")
            position_ids[position["code"]] = existing["id"]
        else:
            # Находим подходящую функцию (если есть)
            function_id = None
            if "директор" in position["name"].lower():
                cursor.execute("SELECT id FROM functions WHERE name LIKE '%управление%' LIMIT 1")
                function = cursor.fetchone()
                if function:
                    function_id = function["id"]
            
            # Создаем должность
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
            new_id = cursor.lastrowid
            logger.info(f"Создана должность {position['name']} с ID: {new_id}")
            position_ids[position["code"]] = new_id
    
    conn.commit()
    return position_ids

def create_board_members(board_id, position_ids):
    """Создает членов совета учредителей"""
    logger.info("Создание членов совета учредителей...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверим существующих членов совета
    cursor.execute(
        """
        SELECT s.id FROM staff s
        JOIN staff_positions sp ON s.id = sp.staff_id
        WHERE sp.position_id = ?
        """, 
        (position_ids["BOARD-MEMBER"],)
    )
    existing = cursor.fetchall()
    
    if existing:
        logger.info(f"Уже существует {len(existing)} членов совета учредителей")
        return [row["id"] for row in existing]
    
    # Создаем 5 членов совета учредителей
    board_member_ids = []
    first_names = ["Александр", "Михаил", "Сергей", "Виктор", "Дмитрий"]
    last_names = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов"]
    
    for i in range(5):
        # Создаем сотрудника
        cursor.execute(
            """
            INSERT INTO staff (
                email, first_name, last_name, phone, description
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                f"board{i+1}@ofsglobal.ru",
                first_names[i],
                last_names[i],
                f"+7495123456{i}",
                f"Учредитель #{i+1}"
            )
        )
        staff_id = cursor.lastrowid
        board_member_ids.append(staff_id)
        
        # Создаем связь с должностью
        cursor.execute(
            """
            INSERT INTO staff_positions (
                staff_id, position_id, is_primary, is_active, start_date
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                staff_id,
                position_ids["BOARD-MEMBER"],
                1, # основная должность
                1, # активна
                datetime.now().strftime("%Y-%m-%d")
            )
        )
        
        logger.info(f"Создан член совета учредителей {first_names[i]} {last_names[i]} с ID: {staff_id}")
    
    conn.commit()
    return board_member_ids

def create_ceo(position_ids):
    """Создает генерального директора"""
    logger.info("Создание генерального директора...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверим существующего CEO
    cursor.execute(
        """
        SELECT s.id FROM staff s
        JOIN staff_positions sp ON s.id = sp.staff_id
        WHERE sp.position_id = ?
        """, 
        (position_ids["CEO"],)
    )
    existing = cursor.fetchone()
    
    if existing:
        logger.info(f"Генеральный директор уже существует с ID: {existing['id']}")
        return existing["id"]
    
    # Создаем генерального директора
    cursor.execute(
        """
        INSERT INTO staff (
            email, first_name, last_name, phone, description
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            "ceo@ofsglobal.ru",
            "Андрей",
            "Волков",
            "+74951234567",
            "Генеральный директор компании"
        )
    )
    ceo_id = cursor.lastrowid
    
    # Создаем связь с должностью
    cursor.execute(
        """
        INSERT INTO staff_positions (
            staff_id, position_id, is_primary, is_active, start_date
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            ceo_id,
            position_ids["CEO"],
            1, # основная должность
            1, # активна
            datetime.now().strftime("%Y-%m-%d")
        )
    )
    
    logger.info(f"Создан генеральный директор с ID: {ceo_id}")
    
    conn.commit()
    return ceo_id

def create_directors(position_ids, ceo_id):
    """Создает директоров компании"""
    logger.info("Создание директоров компании...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    directors = [
        {
            "code": "CFO",
            "email": "cfo@ofsglobal.ru",
            "first_name": "Елена",
            "last_name": "Морозова",
            "phone": "+74951234568",
            "description": "Финансовый директор"
        },
        {
            "code": "CCO",
            "email": "cco@ofsglobal.ru",
            "first_name": "Игорь",
            "last_name": "Соколов",
            "phone": "+74951234569",
            "description": "Коммерческий директор"
        },
        {
            "code": "CTO",
            "email": "cto@ofsglobal.ru",
            "first_name": "Павел",
            "last_name": "Орлов",
            "phone": "+74951234570",
            "description": "Технический директор"
        }
    ]
    
    director_ids = {}
    
    for director in directors:
        # Проверяем существование
        cursor.execute(
            """
            SELECT s.id FROM staff s
            JOIN staff_positions sp ON s.id = sp.staff_id
            WHERE sp.position_id = ?
            """, 
            (position_ids[director["code"]],)
        )
        existing = cursor.fetchone()
        
        if existing:
            logger.info(f"Директор {director['code']} уже существует с ID: {existing['id']}")
            director_ids[director["code"]] = existing["id"]
            continue
        
        # Создаем директора
        cursor.execute(
            """
            INSERT INTO staff (
                email, first_name, last_name, phone, description
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                director["email"],
                director["first_name"],
                director["last_name"],
                director["phone"],
                director["description"]
            )
        )
        staff_id = cursor.lastrowid
        director_ids[director["code"]] = staff_id
        
        # Создаем связь с должностью
        cursor.execute(
            """
            INSERT INTO staff_positions (
                staff_id, position_id, is_primary, is_active, start_date
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                staff_id,
                position_ids[director["code"]],
                1, # основная должность
                1, # активна
                datetime.now().strftime("%Y-%m-%d")
            )
        )
        
        logger.info(f"Создан директор {director['first_name']} {director['last_name']} с ID: {staff_id}")
    
    conn.commit()
    return director_ids

def create_functional_relations(board_member_ids, ceo_id, director_ids):
    """Создает функциональные отношения между руководством"""
    logger.info("Создание функциональных отношений...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверим существующие отношения между советом и CEO
    cursor.execute(
        """
        SELECT id FROM functional_relations 
        WHERE subordinate_id = ? AND relation_type = 'governance'
        """, 
        (ceo_id,)
    )
    existing = cursor.fetchall()
    
    if not existing:
        # Создаем отношения между каждым членом совета и CEO
        for board_member_id in board_member_ids:
            cursor.execute(
                """
                INSERT INTO functional_relations (
                    manager_id, subordinate_id, relation_type, description
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    board_member_id,
                    ceo_id,
                    "governance",
                    "Корпоративное управление"
                )
            )
        logger.info(f"Созданы отношения GOVERNANCE между членами совета и CEO")
    else:
        logger.info(f"Отношения между советом и CEO уже существуют")
    
    # Проверим существующие отношения между CEO и директорами
    for director_code, director_id in director_ids.items():
        cursor.execute(
            """
            SELECT id FROM functional_relations 
            WHERE manager_id = ? AND subordinate_id = ? AND relation_type = 'administrative'
            """, 
            (ceo_id, director_id)
        )
        existing = cursor.fetchone()
        
        if not existing:
            # Создаем отношение между CEO и директором
            cursor.execute(
                """
                INSERT INTO functional_relations (
                    manager_id, subordinate_id, relation_type, description
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    ceo_id,
                    director_id,
                    "administrative",
                    "Административное подчинение"
                )
            )
            logger.info(f"Создано отношение ADMINISTRATIVE между CEO и {director_code}")
        else:
            logger.info(f"Отношение между CEO и {director_code} уже существует")
    
    # Создаем несколько отношений STRATEGIC между членами совета
    chairman_id = board_member_ids[0]  # Первый член совета - председатель
    
    for i in range(1, len(board_member_ids)):
        cursor.execute(
            """
            SELECT id FROM functional_relations 
            WHERE manager_id = ? AND subordinate_id = ? AND relation_type = 'strategic'
            """, 
            (chairman_id, board_member_ids[i])
        )
        existing = cursor.fetchone()
        
        if not existing:
            cursor.execute(
                """
                INSERT INTO functional_relations (
                    manager_id, subordinate_id, relation_type, description
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    chairman_id,
                    board_member_ids[i],
                    "strategic",
                    "Стратегическое управление внутри совета"
                )
            )
    
    logger.info(f"Созданы стратегические отношения внутри совета учредителей")
    
    conn.commit()

def main():
    try:
        board_id = create_board()
        position_ids = create_executive_positions()
        board_member_ids = create_board_members(board_id, position_ids)
        ceo_id = create_ceo(position_ids)
        director_ids = create_directors(position_ids, ceo_id)
        create_functional_relations(board_member_ids, ceo_id, director_ids)
        
        logger.info("Создание структуры руководства успешно завершено!")
    except Exception as e:
        logger.error(f"Ошибка при создании структуры руководства: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 