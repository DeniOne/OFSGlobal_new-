import sqlite3
import os
import sys

def clean_orphan_hierarchy_relations(conn, cursor):
    """
    Удаляет "осиротевшие" записи из таблицы hierarchy_relations,
    т.е. те, у которых superior_position_id или subordinate_position_id
    не существуют в таблице positions.
    """
    print("\nПроверяем и удаляем осиротевшие иерархические связи...")
    
    # Сначала посчитаем, сколько записей будем удалять
    cursor.execute("""
        SELECT COUNT(*) FROM hierarchy_relations
        WHERE superior_position_id NOT IN (SELECT id FROM positions)
           OR subordinate_position_id NOT IN (SELECT id FROM positions)
    """)
    count_to_delete = cursor.fetchone()[0]
    
    if count_to_delete > 0:
        print(f"Найдено {count_to_delete} осиротевших связей. Удаляем...")
        # Удаляем записи
        cursor.execute("""
            DELETE FROM hierarchy_relations
            WHERE superior_position_id NOT IN (SELECT id FROM positions)
               OR subordinate_position_id NOT IN (SELECT id FROM positions)
        """)
        conn.commit()
        print("Осиротевшие связи успешно удалены.")
    else:
        print("Осиротевшие связи не найдены.")

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
            },
            # Добавляем таблицу hierarchy_relations для иерархических связей между должностями
            {
                "name": "hierarchy_relations",
                "schema": """
                CREATE TABLE IF NOT EXISTS hierarchy_relations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    superior_position_id INTEGER NOT NULL,
                    subordinate_position_id INTEGER NOT NULL,
                    priority INTEGER NOT NULL DEFAULT 1,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    description TEXT,
                    extra_field1 TEXT,
                    extra_field2 TEXT,
                    extra_int1 INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (superior_position_id) REFERENCES positions(id) ON DELETE CASCADE,
                    FOREIGN KEY (subordinate_position_id) REFERENCES positions(id) ON DELETE CASCADE
                )
                """
            },
            # Добавляем таблицу unit_management для связей между должностями и подразделениями/отделами
            {
                "name": "unit_management",
                "schema": """
                CREATE TABLE IF NOT EXISTS unit_management (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    position_id INTEGER NOT NULL,
                    managed_type VARCHAR(20) NOT NULL,
                    managed_id INTEGER NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    description TEXT,
                    extra_field1 TEXT,
                    extra_field2 TEXT,
                    extra_int1 INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE
                )
                """
            },
            # Добавляем таблицу functional_assignments для функциональных назначений
            {
                "name": "functional_assignments",
                "schema": """
                CREATE TABLE IF NOT EXISTS functional_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    position_id INTEGER NOT NULL,
                    function_id INTEGER NOT NULL,
                    percentage INTEGER DEFAULT 100,
                    is_primary INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE,
                    FOREIGN KEY (function_id) REFERENCES functions(id) ON DELETE CASCADE
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
                    # Индексы для новых таблиц hierarchy_relations
                    elif table_name == "hierarchy_relations":
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_superior_id ON {table_name}(superior_position_id)")
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_subordinate_id ON {table_name}(subordinate_position_id)")
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_priority ON {table_name}(priority)")
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_is_active ON {table_name}(is_active)")
                    # Индексы для новых таблиц unit_management
                    elif table_name == "unit_management":
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_position_id ON {table_name}(position_id)")
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_managed_type ON {table_name}(managed_type)")
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_managed_id ON {table_name}(managed_id)")
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_is_active ON {table_name}(is_active)")
                    # Индексы для таблицы functional_assignments
                    elif table_name == "functional_assignments":
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_position_id ON {table_name}(position_id)")
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_function_id ON {table_name}(function_id)")
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_is_primary ON {table_name}(is_primary)")
                    
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
        
        # <<-- ОЧИСТКА ОСИРОТЕВШИХ СВЯЗЕЙ -->>
        # Вызываем функцию очистки ПОСЛЕ проверки/создания таблиц, но ДО добавления тестовых данных
        clean_orphan_hierarchy_relations(conn, cursor)

        # <<-- ИСПРАВЛЕНИЕ АТРИБУТОВ ДОЛЖНОСТЕЙ -->>
        print("\nПроверяем и исправляем атрибуты должностей в таблице positions...")
        attribute_updates = {
            # Старое значение из БД : Новое значение из Enum PositionAttribute
            "Директор": "Директор Направления",
            "Руководитель отдела": "Руководитель Отдела",
            "Руководитель департамента": "Руководитель Департамента",
            "Высшее руководство": "Высшее Руководство (Генеральный Директор)",
            "Совет Учредителей": "Совет Учредителей", # На всякий случай, если было другое
            "Специалист": "Специалист", # И это тоже
            # Добавь сюда другие неправильные значения, если они всплывут в логах
        }
        updated_count = 0
        for old_attr, new_attr in attribute_updates.items():
            try:
                cursor.execute("UPDATE positions SET attribute = ? WHERE attribute = ?", (new_attr, old_attr))
                # Проверяем, сколько строк было затронуто
                if cursor.rowcount > 0:
                    print(f"  - Обновлено {cursor.rowcount} записей с '{old_attr}' на '{new_attr}'.")
                    updated_count += cursor.rowcount
            except sqlite3.Error as e:
                print(f"Ошибка при обновлении атрибута '{old_attr}' на '{new_attr}': {e}")
        
        if updated_count > 0:
            conn.commit()
            print(f"Исправление атрибутов завершено. Всего обновлено: {updated_count} записей.")
        else:
            print("Атрибуты должностей не требовали исправлений.")
        # <<-- КОНЕЦ ИСПРАВЛЕНИЯ АТРИБУТОВ -->>

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
            
        # <<-- ДОБАВЛЯЕМ ОЧИСТКУ POSITIONS -->>
        print("\nОчищаем таблицу positions перед добавлением тестовых данных...")
        cursor.execute("DELETE FROM positions")
        conn.commit() # Сохраняем удаление
        
        # Проверяем наличие должностей с разными атрибутами
        cursor.execute("SELECT COUNT(*) FROM positions")
        pos_count = cursor.fetchone()[0]
        if pos_count == 0:
            print("\nВ таблице positions нет записей. Добавляем тестовые должности...")
            
            # Получаем ID тестового подразделения и отдела
            cursor.execute("SELECT id FROM divisions LIMIT 1")
            div_id = cursor.fetchone()[0]
            cursor.execute("SELECT id FROM sections LIMIT 1")
            sec_id = cursor.fetchone()[0]
            
            # Добавляем базовые должности с разными атрибутами для тестирования
            cursor.execute("""
            INSERT INTO positions (name, description, is_active, attribute, division_id, section_id)
            VALUES
            ('Генеральный директор', 'Руководитель компании', 1, 'Директор', NULL, NULL),
            ('Финансовый директор', 'Руководитель финансового департамента', 1, 'Директор', ?, NULL),
            ('Руководитель IT-департамента', 'Руководитель IT-департамента', 1, 'Руководитель департамента', ?, NULL),
            ('Руководитель отдела разработки', 'Руководитель отдела разработки', 1, 'Руководитель отдела', ?, ?),
            ('Разработчик', 'Создание ПО', 1, 'Специалист', ?, ?),
            ('Тестировщик', 'Тестирование ПО', 1, 'Специалист', ?, ?);
            """, (div_id, div_id, div_id, sec_id, div_id, sec_id, div_id, sec_id))
            conn.commit()
            print("Тестовые должности добавлены!")
        
        # <<-- ДОБАВЛЯЕМ УДАЛЕНИЕ СТАРЫХ ДАННЫХ -->>
        print("\nОчищаем таблицу hierarchy_relations перед добавлением тестовых данных...")
        cursor.execute("DELETE FROM hierarchy_relations")
        conn.commit() # Сохраняем удаление
        
        # Создание тестовых связей иерархии
        cursor.execute("SELECT COUNT(*) FROM hierarchy_relations")
        hr_count = cursor.fetchone()[0]
        if hr_count == 0:
            # Проверим, что у нас есть должности для создания иерархии
            cursor.execute("SELECT COUNT(*) FROM positions")
            pos_count = cursor.fetchone()[0]
            
            if pos_count >= 2:
                print("\nВ таблице hierarchy_relations нет записей. Добавляем тестовые иерархические связи...")
                
                # Получаем ID должностей для создания иерархии
                cursor.execute("SELECT id FROM positions WHERE attribute = 'Директор' LIMIT 1")
                director_id = cursor.fetchone()
                
                if director_id:
                    director_id = director_id[0]
                    
                    # Получим другие должности
                    cursor.execute("SELECT id, attribute FROM positions WHERE id != ?", (director_id,))
                    other_positions = cursor.fetchall()
                    
                    # Создаем иерархию
                    for pos_id, attribute in other_positions:
                        priority = 1
                        
                        # Для директоров и руководителей департаментов - прямое подчинение гендиректору
                        if attribute in ['Директор', 'Руководитель департамента']:
                            cursor.execute("""
                            INSERT INTO hierarchy_relations 
                            (superior_position_id, subordinate_position_id, priority, description)
                            VALUES (?, ?, ?, ?)
                            """, (director_id, pos_id, priority, f"Подчинение {attribute} генеральному директору"))
                    
                    # Для руководителей отделов - подчинение руководителям департаментов
                    cursor.execute("SELECT id FROM positions WHERE attribute = 'Руководитель департамента' LIMIT 1")
                    dep_head_id = cursor.fetchone()
                    
                    if dep_head_id:
                        dep_head_id = dep_head_id[0]
                        cursor.execute("SELECT id FROM positions WHERE attribute = 'Руководитель отдела'")
                        section_heads = cursor.fetchall()
                        
                        for section_head in section_heads:
                            section_head_id = section_head[0]
                            cursor.execute("""
                            INSERT INTO hierarchy_relations 
                            (superior_position_id, subordinate_position_id, priority, description)
                            VALUES (?, ?, ?, ?)
                            """, (dep_head_id, section_head_id, 1, "Подчинение руководителя отдела руководителю департамента"))
                    
                    # Для специалистов - подчинение руководителям отделов
                    cursor.execute("SELECT id FROM positions WHERE attribute = 'Руководитель отдела' LIMIT 1")
                    section_head_id = cursor.fetchone()
                    
                    if section_head_id:
                        section_head_id = section_head_id[0]
                        cursor.execute("SELECT id FROM positions WHERE attribute = 'Специалист'")
                        specialists = cursor.fetchall()
                        
                        for specialist in specialists:
                            specialist_id = specialist[0]
                            cursor.execute("""
                            INSERT INTO hierarchy_relations 
                            (superior_position_id, subordinate_position_id, priority, description)
                            VALUES (?, ?, ?, ?)
                            """, (section_head_id, specialist_id, 1, "Подчинение специалиста руководителю отдела"))
                    
                    conn.commit()
                    print("Тестовые иерархические связи добавлены!")
        
        # Создание тестовых связей управления подразделениями, если таблица только что создана
        cursor.execute("SELECT COUNT(*) FROM unit_management")
        um_count = cursor.fetchone()[0]
        if um_count == 0:
            # Проверим, что у нас есть должности и подразделения для создания связей
            cursor.execute("SELECT COUNT(*) FROM positions")
            pos_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM divisions")
            div_count = cursor.fetchone()[0]
            
            if pos_count > 0 and div_count > 0:
                print("\nВ таблице unit_management нет записей. Добавляем тестовые связи управления...")
                
                # Получаем ID должностей руководителей для создания связей
                cursor.execute("SELECT id, name FROM positions WHERE attribute IN ('Директор', 'Руководитель департамента')")
                managers = cursor.fetchall()
                
                # Получаем департаменты
                cursor.execute("SELECT id, name FROM divisions")
                divisions = cursor.fetchall()
                
                # Получаем отделы
                cursor.execute("SELECT id, name, division_id FROM sections")
                sections = cursor.fetchall()
                
                # Создаем связи управления
                for manager_id, manager_name in managers:
                    # Если это генеральный директор - управляет всеми департаментами
                    if "Генеральный" in manager_name:
                        for div_id, div_name in divisions:
                            cursor.execute("""
                            INSERT INTO unit_management 
                            (position_id, managed_type, managed_id, description)
                            VALUES (?, ?, ?, ?)
                            """, (manager_id, "division", div_id, f"Управление {div_name}"))
                    
                    # Если это руководитель департамента - управляет своим департаментом и его отделами
                    elif "департамента" in manager_name.lower():
                        # Пытаемся найти подходящий департамент по имени
                        for div_id, div_name in divisions:
                            if div_name.lower() in manager_name.lower() or manager_name.lower() in div_name.lower():
                                cursor.execute("""
                                INSERT INTO unit_management 
                                (position_id, managed_type, managed_id, description)
                                VALUES (?, ?, ?, ?)
                                """, (manager_id, "division", div_id, f"Управление {div_name}"))
                                
                                # Также управляет отделами своего департамента
                                for sec_id, sec_name, sec_div_id in sections:
                                    if sec_div_id == div_id:
                                        cursor.execute("""
                                        INSERT INTO unit_management 
                                        (position_id, managed_type, managed_id, description)
                                        VALUES (?, ?, ?, ?)
                                        """, (manager_id, "section", sec_id, f"Управление {sec_name}"))
                
                # Руководители отделов управляют своими отделами
                cursor.execute("SELECT id, name FROM positions WHERE attribute = 'Руководитель отдела'")
                section_managers = cursor.fetchall()
                
                for manager_id, manager_name in section_managers:
                    for sec_id, sec_name, sec_div_id in sections:
                        if sec_name.lower() in manager_name.lower() or manager_name.lower() in sec_name.lower():
                            cursor.execute("""
                            INSERT INTO unit_management 
                            (position_id, managed_type, managed_id, description)
                            VALUES (?, ?, ?, ?)
                            """, (manager_id, "section", sec_id, f"Управление {sec_name}"))
                
                conn.commit()
                print("Тестовые связи управления добавлены!")
        
        print("\nПроверка и исправление таблиц завершены. База данных обновлена.")
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_tables() 