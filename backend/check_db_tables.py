import sqlite3
import os
import sys

def check_tables():
    """
    Напрямую проверяет содержимое таблиц positions и hierarchy_relations в базе данных.
    """
    print("Проверяем содержимое таблиц positions и hierarchy_relations...")
    
    # Путь к базе данных
    db_path = os.path.join(os.path.dirname(__file__), "full_api_new.db")
    
    if not os.path.exists(db_path):
        print(f"Ошибка: файл базы данных не найден по пути {db_path}")
        sys.exit(1)
    
    try:
        # Подключаемся к БД
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Чтобы получать результаты в виде словарей
        cursor = conn.cursor()
        
        # Проверяем positions
        print("\n=== ТАБЛИЦА: positions ===")
        cursor.execute("SELECT COUNT(*) as count FROM positions")
        count = cursor.fetchone()["count"]
        print(f"Количество записей: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, name, attribute, division_id, section_id FROM positions LIMIT 100")
            positions = cursor.fetchall()
            
            print("Найденные записи:")
            for pos in positions:
                print(f"ID: {pos['id']}, Название: {pos['name']}, Атрибут: {pos['attribute']}, "
                      f"Подразделение: {pos['division_id']}, Отдел: {pos['section_id']}")
        
        # Проверяем hierarchy_relations
        print("\n=== ТАБЛИЦА: hierarchy_relations ===")
        cursor.execute("SELECT COUNT(*) as count FROM hierarchy_relations")
        count = cursor.fetchone()["count"]
        print(f"Количество записей: {count}")
        
        if count > 0:
            cursor.execute("""
                SELECT 
                    hr.id, 
                    hr.superior_position_id, 
                    p1.name as superior_name,
                    hr.subordinate_position_id, 
                    p2.name as subordinate_name,
                    hr.priority
                FROM 
                    hierarchy_relations hr
                LEFT JOIN 
                    positions p1 ON hr.superior_position_id = p1.id
                LEFT JOIN 
                    positions p2 ON hr.subordinate_position_id = p2.id
                LIMIT 100
            """)
            relations = cursor.fetchall()
            
            print("Найденные связи:")
            for rel in relations:
                print(f"ID: {rel['id']}, "
                      f"Руководитель ID: {rel['superior_position_id']} ('{rel['superior_name'] or 'Н/Д'}'), "
                      f"Подчиненный ID: {rel['subordinate_position_id']} ('{rel['subordinate_name'] or 'Н/Д'}'), "
                      f"Приоритет: {rel['priority']}")
                      
            # Дополнительная проверка целостности
            print("\n=== ПРОВЕРКА ЦЕЛОСТНОСТИ ДАННЫХ ===")
            cursor.execute("""
                SELECT hr.id, hr.superior_position_id, hr.subordinate_position_id 
                FROM hierarchy_relations hr
                LEFT JOIN positions p1 ON hr.superior_position_id = p1.id
                WHERE p1.id IS NULL
                LIMIT 10
            """)
            invalid_super = cursor.fetchall()
            if invalid_super:
                print("ОШИБКА: Обнаружены связи с отсутствующими руководящими должностями:")
                for rel in invalid_super:
                    print(f"  - Связь ID: {rel['id']}, Отсутствует должность с ID: {rel['superior_position_id']}")
            else:
                print("✓ Все руководящие должности найдены в таблице positions.")
            
            cursor.execute("""
                SELECT hr.id, hr.superior_position_id, hr.subordinate_position_id 
                FROM hierarchy_relations hr
                LEFT JOIN positions p2 ON hr.subordinate_position_id = p2.id
                WHERE p2.id IS NULL
                LIMIT 10
            """)
            invalid_sub = cursor.fetchall()
            if invalid_sub:
                print("ОШИБКА: Обнаружены связи с отсутствующими подчиненными должностями:")
                for rel in invalid_sub:
                    print(f"  - Связь ID: {rel['id']}, Отсутствует должность с ID: {rel['subordinate_position_id']}")
            else:
                print("✓ Все подчиненные должности найдены в таблице positions.")

        # Если мы получаем должности, но API возвращает пустые списки, проверим реальные SQL запросы, используемые в API
        if count > 0:
            print("\n=== ТЕСТ SQL ЗАПРОСА ИЗ API ===")
            
            # Запрос аналогичный тому, что используется в GET /positions/
            print("Тест запроса GET /positions/:")
            cursor.execute("""
                SELECT * FROM positions 
                ORDER BY name
                LIMIT 100
            """)
            api_positions = cursor.fetchall()
            print(f"Запрос вернул {len(api_positions)} должностей.")
            
            # Запрос аналогичный тому, что используется в GET /hierarchy/hierarchy-relations/
            print("\nТест запроса GET /hierarchy/hierarchy-relations/:")
            cursor.execute("""
                SELECT hr.*, 
                    p1.name as superior_position_name, 
                    p1.attribute as superior_position_attribute,
                    p2.name as subordinate_position_name, 
                    p2.attribute as subordinate_position_attribute
                FROM hierarchy_relations hr
                LEFT JOIN positions p1 ON hr.superior_position_id = p1.id
                LEFT JOIN positions p2 ON hr.subordinate_position_id = p2.id
                ORDER BY hr.priority, hr.id
                LIMIT 100
            """)
            api_relations = cursor.fetchall()
            print(f"Запрос вернул {len(api_relations)} связей.")
        
        print("\nПроверка завершена.")
    
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_tables() 