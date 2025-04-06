import sqlite3
import sys

def check_table_structure(db_path, table_name):
    """Проверяет структуру указанной таблицы и выводит все поля"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Структура таблицы {table_name}:")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    for col in columns:
        col_id, name, type_name, not_null, default_val, is_pk = col
        print(f"  {col_id}: {name} ({type_name}), NOT NULL: {bool(not_null)}, DEFAULT: {default_val}, PRIMARY KEY: {bool(is_pk)}")
    
    conn.close()

if __name__ == "__main__":
    db_path = "full_api_new.db"
    
    if len(sys.argv) > 1:
        tables = sys.argv[1:]
    else:
        # Получаем список всех таблиц в базе
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
        tables = [table[0] for table in cursor.fetchall()]
        conn.close()
    
    for table in tables:
        check_table_structure(db_path, table)
        print() 