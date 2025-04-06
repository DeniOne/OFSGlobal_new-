import sqlite3

def get_db_connection():
    """Создает подключение к базе данных"""
    conn = sqlite3.connect("full_api_new.db")
    conn.row_factory = sqlite3.Row
    return conn

def main():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Открываем файл для записи
    with open("board_check_results.txt", "w", encoding="utf-8") as f:
        # Проверяем запись Совета учредителей
        f.write("=== СОВЕТ УЧРЕДИТЕЛЕЙ ===\n")
        cursor.execute('SELECT id, name, code, org_type FROM organizations WHERE org_type = "board"')
        for row in cursor.fetchall():
            f.write(f"ID: {row['id']}, Название: {row['name']}, Код: {row['code']}, Тип: {row['org_type']}\n")
        
        # Проверяем должности руководства
        f.write("\n=== ДОЛЖНОСТИ РУКОВОДСТВА ===\n")
        cursor.execute('SELECT id, name, code, description FROM positions WHERE name LIKE "%директор%" OR code = "BOARD-MEMBER"')
        for row in cursor.fetchall():
            f.write(f"ID: {row['id']}, Название: {row['name']}, Код: {row['code']}\n")
            f.write(f"  Описание: {row['description']}\n")
        
        # Проверяем членов совета учредителей
        f.write("\n=== ЧЛЕНЫ СОВЕТА УЧРЕДИТЕЛЕЙ ===\n")
        cursor.execute('''
            SELECT s.id, s.first_name, s.last_name, s.email, p.name 
            FROM staff s 
            JOIN staff_positions sp ON s.id = sp.staff_id 
            JOIN positions p ON sp.position_id = p.id 
            WHERE p.code = "BOARD-MEMBER"
        ''')
        for row in cursor.fetchall():
            f.write(f"ID: {row['id']}, Имя: {row['first_name']} {row['last_name']}, Email: {row['email']}, Должность: {row['name']}\n")
        
        # Проверяем топ-менеджмент
        f.write("\n=== ТОП-МЕНЕДЖМЕНТ ===\n")
        cursor.execute('''
            SELECT s.id, s.first_name, s.last_name, s.email, p.name 
            FROM staff s 
            JOIN staff_positions sp ON s.id = sp.staff_id 
            JOIN positions p ON sp.position_id = p.id 
            WHERE p.code IN ("CEO", "CFO", "CCO", "CTO")
        ''')
        for row in cursor.fetchall():
            f.write(f"ID: {row['id']}, Имя: {row['first_name']} {row['last_name']}, Email: {row['email']}, Должность: {row['name']}\n")
        
        # Проверяем функциональные отношения
        f.write("\n=== ФУНКЦИОНАЛЬНЫЕ ОТНОШЕНИЯ ===\n")
        cursor.execute('''
            SELECT 
                m.first_name || ' ' || m.last_name AS manager,
                s.first_name || ' ' || s.last_name AS subordinate,
                r.relation_type,
                r.description
            FROM functional_relations r
            JOIN staff m ON r.manager_id = m.id
            JOIN staff s ON r.subordinate_id = s.id
            WHERE r.relation_type IN ("governance", "administrative", "strategic")
        ''')
        
        relation_types = {}
        for row in cursor.fetchall():
            relation_type = row['relation_type']
            if relation_type not in relation_types:
                relation_types[relation_type] = []
            relation_types[relation_type].append({
                'manager': row['manager'],
                'subordinate': row['subordinate'],
                'description': row['description']
            })
        
        for relation_type, relations in relation_types.items():
            f.write(f"\n{relation_type.upper()}:\n")
            for relation in relations:
                f.write(f"  {relation['manager']} → {relation['subordinate']}\n")
                if relation['description']:
                    f.write(f"    Описание: {relation['description']}\n")
    
    conn.close()
    print("Результаты записаны в файл board_check_results.txt")

if __name__ == "__main__":
    main() 