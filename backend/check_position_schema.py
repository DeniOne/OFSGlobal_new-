import sqlite3
import os
import sys

def check_schema():
    """Подключается к БД и выводит схему таблицы positions."""
    print("Проверяем схему таблицы 'positions'...")
    
    # Определяем путь к файлу БД относительно текущего скрипта
    script_dir = os.path.dirname(__file__)
    db_path = os.path.join(script_dir, "full_api_new.db")
    
    if not os.path.exists(db_path):
        print(f"Ошибка: файл базы данных не найден по пути {db_path}")
        sys.exit(1)
        
    conn = None  # Инициализируем conn
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Подключено к БД: {db_path}")
        
        # Выполняем PRAGMA для получения информации о таблице
        cursor.execute("PRAGMA table_info(positions)")
        columns = cursor.fetchall()
        
        if not columns:
            print("Таблица 'positions' не найдена или пуста.")
        else:
            print("\nСтруктура таблицы 'positions':")
            print("CID | Имя колонки        | Тип данных   | NOT NULL | Значение по умолчанию | PK")
            print("-----------------------------------------------------------------------------")
            for col in columns:
                cid, name, dtype, notnull, dflt_value, pk = col
                print(f"{cid:<3} | {name:<18} | {dtype:<12} | {notnull:<8} | {str(dflt_value):<21} | {pk}")
            
            # Проверяем наличие колонки 'attribute'
            column_names = [col[1] for col in columns]
            if 'attribute' in column_names:
                print("\n✅ Колонка 'attribute' найдена.")
            else:
                print("\n❌ Колонка 'attribute' НЕ найдена.")
                
    except sqlite3.Error as e:
        print(f"\nОшибка SQLite: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()
            print("\nСоединение с БД закрыто.")

if __name__ == "__main__":
    check_schema() 