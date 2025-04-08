import sqlite3
import os
import sys

def check_divisions_table():
    """
    Проверяет, существует ли таблица divisions и создает её, если отсутствует.
    Также проверяет, правильная ли структура таблицы.
    """
    print("Проверка таблицы divisions в базе данных...")
    
    # Путь к базе данных
    db_path = os.path.join(os.path.dirname(__file__), "full_api_new.db")
    
    if not os.path.exists(db_path):
        print(f"Ошибка: файл базы данных не найден по пути {db_path}")
        sys.exit(1)
    
    try:
        # Подключаемся к БД
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем существование таблицы divisions
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='divisions'")
        if not cursor.fetchone():
            print("Таблица divisions не найдена. Создаем...")
            
            # Создаем таблицу divisions
            cursor.execute("""
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
            """)
            
            # Создаем триггер для обновления даты
            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_division_timestamp 
            AFTER UPDATE ON divisions
            FOR EACH ROW
            BEGIN
                UPDATE divisions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
            END
            """)
            
            # Создаем индексы
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_divisions_organization_id ON divisions(organization_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_divisions_parent_id ON divisions(parent_id)")
            
            conn.commit()
            print("Таблица divisions успешно создана!")
        else:
            print("Таблица divisions существует, проверяем структуру...")
            
            # Проверяем, есть ли необходимые поля
            cursor.execute("PRAGMA table_info(divisions)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            required_columns = ["id", "name", "code", "organization_id", "description", "is_active", "created_at", "updated_at"]
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"Внимание! В таблице divisions отсутствуют следующие обязательные колонки: {', '.join(missing_columns)}")
                
                # Пытаемся добавить отсутствующие колонки
                for col in missing_columns:
                    try:
                        if col == "organization_id":
                            cursor.execute("ALTER TABLE divisions ADD COLUMN organization_id INTEGER NOT NULL DEFAULT 1")
                        elif col in ["created_at", "updated_at"]:
                            cursor.execute(f"ALTER TABLE divisions ADD COLUMN {col} TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                        elif col == "is_active":
                            cursor.execute("ALTER TABLE divisions ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")
                        elif col == "code":
                            cursor.execute("ALTER TABLE divisions ADD COLUMN code TEXT")
                        else:
                            cursor.execute(f"ALTER TABLE divisions ADD COLUMN {col} TEXT")
                        print(f"Добавлена колонка {col}")
                    except sqlite3.OperationalError as e:
                        print(f"Не удалось добавить колонку {col}: {e}")
                
                conn.commit()
            else:
                print("Все обязательные колонки присутствуют.")
        
        # Выводим для проверки текущую структуру таблицы
        cursor.execute("PRAGMA table_info(divisions)")
        columns = cursor.fetchall()
        print("\nТекущие колонки таблицы divisions:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})" + (" [NOT NULL]" if col[3] else ""))
        
        # Выводим количество записей
        cursor.execute("SELECT COUNT(*) FROM divisions")
        count = cursor.fetchone()[0]
        print(f"\nКоличество записей в таблице divisions: {count}")
        
        print("\nОперация проверки завершена успешно.")
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_divisions_table() 