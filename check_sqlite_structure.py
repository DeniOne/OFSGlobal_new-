#!/usr/bin/env python
"""
Скрипт для проверки структуры базы данных SQLite.
Выводит список таблиц и примеры данных в каждой таблице.
"""

import sqlite3
import os

# Путь к базе данных SQLite
DB_PATH = "backend/full_api_new.db"

def main():
    if not os.path.exists(DB_PATH):
        print(f"Ошибка: База данных не найдена по пути {DB_PATH}")
        return
    
    try:
        # Подключение к базе данных
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Получение списка таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if not tables:
            print("В базе данных нет таблиц!")
            return
        
        print(f"Найдено {len(tables)} таблиц в базе данных:")
        for table in tables:
            print(f"\n--- Таблица: {table} ---")
            
            # Получение информации о структуре таблицы
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            print("Структура:")
            for col in columns:
                print(f"  {col[1]} ({col[2]}){' NOT NULL' if col[3] else ''}{' PRIMARY KEY' if col[5] else ''}")
            
            # Получение примера данных
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            rows = cursor.fetchall()
            if rows:
                print("\nПример данных:")
                for row in rows:
                    print(f"  {row}")
            else:
                print("\nТаблица не содержит данных.")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main() 