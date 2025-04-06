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
logger = logging.getLogger("matrix_relations_creation")

DB_PATH = "full_api_new.db"

def get_db_connection():
    """Создает подключение к базе данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_existing_matrix_relations():
    """Проверяет существующие матричные отношения"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM functional_relations 
        WHERE extra_field1 IN ('FUNCTIONAL', 'REPORTING')
    """)
    count = cursor.fetchone()[0]
    
    conn.close()
    return count > 0

def get_staff_by_position_type(position_type):
    """Получает сотрудников по типу должности"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.id, s.first_name, s.last_name 
        FROM staff s
        JOIN staff_positions sp ON s.id = sp.staff_id
        JOIN positions p ON sp.position_id = p.id
        WHERE p.name LIKE ?
        AND sp.is_primary = 1
    """, (f"%{position_type}%",))
    
    staff = cursor.fetchall()
    conn.close()
    return staff

def get_staff_by_function(function_name):
    """Получает сотрудников по назначенной функции"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.id, s.first_name, s.last_name 
        FROM staff s
        JOIN staff_functions sf ON s.id = sf.staff_id
        JOIN functions f ON sf.function_id = f.id
        WHERE f.name LIKE ?
    """, (f"%{function_name}%",))
    
    staff = cursor.fetchall()
    conn.close()
    return staff

def get_all_staff():
    """Получает список всех сотрудников"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, first_name, last_name FROM staff")
    staff = cursor.fetchall()
    
    conn.close()
    return staff

def create_matrix_relations():
    """Создает матричные функциональные и отчетные отношения между сотрудниками"""
    logger.info("Создание матричных отношений...")
    
    # Проверяем, есть ли уже такие отношения
    if check_existing_matrix_relations():
        logger.info("Матричные отношения уже созданы")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Функциональные отношения между руководителями направлений и сотрудниками
    # Найдем руководителей функциональных направлений
    functional_leads = get_staff_by_position_type("руководитель")
    if not functional_leads:
        logger.warning("Не найдены руководители функциональных направлений")
    
    # Найдем сотрудников с различными функциями
    developers = get_staff_by_function("Разработка")
    testers = get_staff_by_function("Тестирование")
    analysts = get_staff_by_function("Аналитика")
    
    # Для каждого руководителя создадим функциональные отношения с подходящими сотрудниками
    relations_created = 0
    
    for lead in functional_leads:
        # Выберем случайную группу сотрудников для этого руководителя
        target_group = random.choice([developers, testers, analysts])
        
        if not target_group:
            continue
            
        # Выберем от 1 до 3 случайных сотрудников из группы
        num_staff = min(len(target_group), random.randint(1, 3))
        selected_staff = random.sample(target_group, num_staff)
        
        for staff in selected_staff:
            if lead["id"] == staff["id"]:
                continue  # Пропускаем создание отношения с самим собой
                
            # Создаем функциональное отношение
            cursor.execute(
                """
                INSERT INTO functional_relations (
                    manager_id, subordinate_id, relation_type, description, start_date, extra_field1
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    lead["id"],
                    staff["id"],
                    "functional", # Используем существующий тип
                    "Функциональное руководство",
                    datetime.now().strftime("%Y-%m-%d"),
                    "FUNCTIONAL"
                )
            )
            
            logger.info(f"Создано FUNCTIONAL отношение: {lead['first_name']} {lead['last_name']} -> {staff['first_name']} {staff['last_name']}")
            relations_created += 1
    
    # 2. Отчетные отношения между сотрудниками проектов и руководителями проектов
    # Имитируем наличие проектных команд, выбирая случайных сотрудников
    all_staff = get_all_staff()
    
    # Выберем несколько "руководителей проектов" из всех сотрудников
    num_project_leads = min(len(all_staff) // 3, 2)
    project_leads = random.sample(all_staff, num_project_leads)
    
    for lead in project_leads:
        # Выберем от 2 до 5 случайных сотрудников для проектной команды
        num_team_members = min(len(all_staff) - 1, random.randint(2, 5))
        potential_team = [s for s in all_staff if s["id"] != lead["id"]]
        team_members = random.sample(potential_team, num_team_members)
        
        for member in team_members:
            # Создаем отчетное отношение
            cursor.execute(
                """
                INSERT INTO functional_relations (
                    manager_id, subordinate_id, relation_type, description, start_date, extra_field1
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    lead["id"],
                    member["id"],
                    "administrative", # Используем существующий тип для отчётов
                    "Проектное подчинение",
                    datetime.now().strftime("%Y-%m-%d"),
                    "REPORTING"
                )
            )
            
            logger.info(f"Создано REPORTING отношение: {lead['first_name']} {lead['last_name']} <- {member['first_name']} {member['last_name']}")
            relations_created += 1
    
    conn.commit()
    conn.close()
    
    if relations_created > 0:
        logger.info(f"Создание матричных отношений завершено, создано {relations_created} отношений")
    else:
        logger.warning("Не удалось создать матричные отношения")

def main():
    try:
        create_matrix_relations()
    except Exception as e:
        logger.error(f"Ошибка при создании матричных отношений: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 