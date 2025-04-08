import sqlite3
import os
import sys

def fix_tables():
    """
    Проверяет и исправляет все необходимые таблицы в базе данных.
    """
    print("Начинаем проверку и исправление таблиц базы данных...")
    
    # Путь к базе данных
    db_path = os.path.join(os.path.dirname(__file__), "full_api_new.db")
    
    if not os.path.exists(db_path):
        print(f"Ошибка: файл базы данных не найден по пути {db_path}")
        sys.exit(1)
    
    try:
        # Подключаемся к БД
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Список таблиц для проверки и их схемы
        tables = [
            {
                "name": "staff",
                "check_column": "user_id",
                "column_type": "INTEGER",
                "message": "Добавляем колонку user_id в таблицу staff"
            },
            {
                "name": "divisions",
                "schema": """
                CREATE TABLE IF NOT EXISTS divisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL UNIQUE,
                    description TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    organization_id INTEGER NOT NULL,
                    parent_id INTEGER,
                    ckp TEXT,
                    extra_field1 TEXT,
                    extra_field2 TEXT,
                    extra_field3 TEXT,
                    extra_int1 INTEGER,
                    extra_int2 INTEGER,
                    extra_date1 DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations(id),
                    FOREIGN KEY (parent_id) REFERENCES divisions(id)
                )
                """
            },
            {
                "name": "sections",
                "schema": """
                CREATE TABLE IF NOT EXISTS sections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT,
                    division_id INTEGER NOT NULL,
                    description TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    ckp TEXT,
                    extra_field1 TEXT,
                    extra_field2 TEXT,
                    extra_field3 TEXT,
                    extra_int1 INTEGER,
                    extra_int2 INTEGER,
                    extra_date1 DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE CASCADE
                )
                """
            }
        ]
        
        # Проверяем каждую таблицу
        for table in tables:
            table_name = table["name"]
            
            # Проверяем существование таблицы
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                print(f"Таблица {table_name} не найдена. Создаем...")
                if "schema" in table:
                    cursor.execute(table["schema"])
                    
                    # Создаем триггер для обновления даты
                    cursor.execute(f"""
                    CREATE TRIGGER IF NOT EXISTS update_{table_name}_timestamp 
                    AFTER UPDATE ON {table_name}
                    FOR EACH ROW
                    BEGIN
                        UPDATE {table_name} SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
                    END
                    """)
                    
                    # Создаем индексы для обычных таблиц
                    if table_name == "divisions":
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_organization_id ON {table_name}(organization_id)")
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_parent_id ON {table_name}(parent_id)")
                    elif table_name == "sections":
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_division_id ON {table_name}(division_id)")
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_code ON {table_name}(code)")
                    
                    conn.commit()
                    print(f"Таблица {table_name} успешно создана!")
            else:
                print(f"Таблица {table_name} существует, проверяем структуру...")
                
                # Проверяем наличие конкретной колонки, если указано
                if "check_column" in table:
                    check_column = table["check_column"]
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    
                    if check_column not in column_names:
                        column_type = table.get("column_type", "TEXT")
                        print(f"{table.get('message', f'Добавляем колонку {check_column} в таблицу {table_name}')}")
                        try:
                            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {check_column} {column_type}")
                            conn.commit()
                            print(f"Колонка {check_column} успешно добавлена!")
                        except sqlite3.OperationalError as e:
                            print(f"Не удалось добавить колонку {check_column}: {e}")
                    else:
                        print(f"Колонка {check_column} уже существует в таблице {table_name}.")
        
        # Проверяем наличие организаций
        cursor.execute("SELECT COUNT(*) FROM organizations")
        org_count = cursor.fetchone()[0]
        if org_count == 0:
            print("\nВ таблице organizations нет записей. Добавляем тестовые организации...")
            # Добавляем базовые организации для тестирования
            cursor.execute("""
            INSERT INTO organizations (name, code, org_type, is_active, description)
            VALUES
            ('ООО "Рога и Копыта"', 'RIK', 'legal_entity', 1, 'Тестовая организация'),
            ('ИП Пупкин', 'IPPUPKIN', 'legal_entity', 1, 'Индивидуальный предприниматель'),
            ('Холдинг "Глобал Тест"', 'GLOBALTEST', 'holding', 1, 'Тестовый холдинг');
            """)
            conn.commit()
            print("Тестовые организации добавлены!")
        
        # Проверяем наличие подразделений
        cursor.execute("SELECT COUNT(*) FROM divisions")
        div_count = cursor.fetchone()[0]
        if div_count == 0:
            print("\nВ таблице divisions нет записей. Добавляем тестовые подразделения...")
            
            # Получаем ID тестовой организации
            cursor.execute("SELECT id FROM organizations LIMIT 1")
            org_id = cursor.fetchone()[0]
            
            # Добавляем базовые подразделения для тестирования
            cursor.execute("""
            INSERT INTO divisions (name, code, organization_id, is_active, description)
            VALUES
            ('Департамент построения организации', 'DPO', ?, 1, 'Основной департамент'),
            ('Департамент информационных технологий', 'IT', ?, 1, 'IT департамент'),
            ('Финансовый департамент', 'FIN', ?, 1, 'Финансы');
            """, (org_id, org_id, org_id))
            conn.commit()
            print("Тестовые подразделения добавлены!")
        
        # Проверяем наличие отделов
        cursor.execute("SELECT COUNT(*) FROM sections")
        sec_count = cursor.fetchone()[0]
        if sec_count == 0:
            print("\nВ таблице sections нет записей. Добавляем тестовые отделы...")
            
            # Получаем ID тестового подразделения
            cursor.execute("SELECT id FROM divisions LIMIT 1")
            div_id = cursor.fetchone()[0]
            
            # Добавляем базовые отделы для тестирования
            cursor.execute("""
            INSERT INTO sections (name, division_id, is_active, description)
            VALUES
            ('Отдел персонала', ?, 1, 'Управление персоналом'),
            ('Отдел разработки', ?, 1, 'Разработка ПО'),
            ('Отдел тестирования', ?, 1, 'Тестирование ПО');
            """, (div_id, div_id, div_id))
            conn.commit()
            print("Тестовые отделы добавлены!")
        
        print("\nПроверка и исправление таблиц завершены. База данных обновлена.")
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_tables() 