import sqlite3
import os
import sys

def check_sections_table():
    """
    Проверяет, существует ли таблица sections и создает её, если отсутствует.
    Также проверяет, правильная ли структура таблицы.
    """
    print("Проверка таблицы sections в базе данных...")
    
    # Путь к базе данных
    db_path = os.path.join(os.path.dirname(__file__), "full_api_new.db")
    
    if not os.path.exists(db_path):
        print(f"Ошибка: файл базы данных не найден по пути {db_path}")
        sys.exit(1)
    
    try:
        # Подключаемся к БД
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем существование таблицы sections
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sections'")
        if not cursor.fetchone():
            print("Таблица sections не найдена. Создаем...")
            
            # Создаем таблицу sections
            cursor.execute("""
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
            """)
            
            # Создаем триггер для обновления даты
            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_section_timestamp 
            AFTER UPDATE ON sections
            FOR EACH ROW
            BEGIN
                UPDATE sections SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
            END
            """)
            
            # Создаем индексы
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sections_division_id ON sections(division_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sections_code ON sections(code)")
            
            conn.commit()
            print("Таблица sections успешно создана!")
        else:
            print("Таблица sections существует, проверяем структуру...")
            
            # Проверяем, есть ли поле division_id
            cursor.execute("PRAGMA table_info(sections)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            required_columns = ["id", "name", "division_id", "description", "is_active", "created_at", "updated_at"]
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"Внимание! В таблице sections отсутствуют следующие обязательные колонки: {', '.join(missing_columns)}")
                
                # Пытаемся добавить отсутствующие колонки
                for col in missing_columns:
                    try:
                        if col == "division_id":
                            cursor.execute("ALTER TABLE sections ADD COLUMN division_id INTEGER NOT NULL DEFAULT 1")
                        elif col in ["created_at", "updated_at"]:
                            cursor.execute(f"ALTER TABLE sections ADD COLUMN {col} TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                        elif col == "is_active":
                            cursor.execute("ALTER TABLE sections ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")
                        else:
                            cursor.execute(f"ALTER TABLE sections ADD COLUMN {col} TEXT")
                        print(f"Добавлена колонка {col}")
                    except sqlite3.OperationalError as e:
                        print(f"Не удалось добавить колонку {col}: {e}")
                
                conn.commit()
            else:
                print("Все обязательные колонки присутствуют.")
        
        # Выводим для проверки текущую структуру таблицы
        cursor.execute("PRAGMA table_info(sections)")
        columns = cursor.fetchall()
        print("\nТекущие колонки таблицы sections:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})" + (" [NOT NULL]" if col[3] else ""))
        
        # Выводим количество записей
        cursor.execute("SELECT COUNT(*) FROM sections")
        count = cursor.fetchone()[0]
        print(f"\nКоличество записей в таблице sections: {count}")
        
        print("\nОперация проверки завершена успешно.")
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_sections_table() 