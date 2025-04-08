import sqlite3
import os
import sys

def add_user_id_column():
    """
    Добавляет колонку user_id в таблицу staff,
    если она еще не существует
    """
    print("Проверяю и добавляю колонку user_id в таблицу staff...")
    
    # Путь к базе данных
    db_path = os.path.join(os.path.dirname(__file__), "full_api_new.db")
    
    if not os.path.exists(db_path):
        print(f"Ошибка: файл базы данных не найден по пути {db_path}")
        sys.exit(1)
    
    try:
        # Подключаемся к БД
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли колонка user_id в таблице staff
        cursor.execute("PRAGMA table_info(staff)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if "user_id" not in column_names:
            # Если колонки нет, добавляем её
            print("Колонка user_id не найдена. Добавляем...")
            cursor.execute("ALTER TABLE staff ADD COLUMN user_id INTEGER")
            conn.commit()
            print("Колонка user_id успешно добавлена!")
        else:
            print("Колонка user_id уже существует в таблице staff.")
        
        # Выводим для проверки все колонки таблицы staff
        cursor.execute("PRAGMA table_info(staff)")
        columns = cursor.fetchall()
        print("Текущие колонки таблицы staff:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        print("\nОперация завершена успешно.")
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_user_id_column() 