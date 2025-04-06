#!/usr/bin/env python
"""
Скрипт для проверки структуры базы данных после миграции.
"""

import sqlite3
import os

# Подключаемся к БД
db_path = "full_api_new.db"
print(f"Проверяем БД: {os.path.abspath(db_path)}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Получаем список таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    if not tables:
        print("В базе данных НЕТ таблиц!")
    else:
        print(f"Таблицы в БД ({len(tables)}):")
        for i, table in enumerate(tables, 1):
            table_name = table[0]
            print(f"{i}. {table_name}")
            
            # Получаем структуру таблицы
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"   Колонки ({len(columns)}):")
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
            
            # Считаем количество записей
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   Записей: {count}")
            print("")
    
except sqlite3.Error as e:
    print(f"Ошибка SQLite: {e}")
finally:
    if 'conn' in locals():
        conn.close()

# Проверяем обе БД
print("Начинаем проверку баз данных...")
# Убираем вызов старой функции, он больше не нужен
# check_db("full_api.db")
check_db("full_api_new.db")
print("\nПроверка завершена.") 