import sqlite3

# Подключение к SQLite базе данных
conn = sqlite3.connect('backend/full_api_new.db')
cursor = conn.cursor()

# Получение списка таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Таблицы в базе данных SQLite (новая):")
for table in tables:
    print(f"- {table[0]}")
    
    # Получение структуры таблицы
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    print(f"  Колонки:")
    for col in columns[:5]:  # Выводим только первые 5 колонок для краткости
        print(f"  - {col[1]} ({col[2]})")
    
    # Количество записей в таблице
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"  Количество записей: {count}")
    print()

# Закрываем соединение
conn.close() 