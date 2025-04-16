#!/usr/bin/env python
"""
Скрипт для сравнения структур баз данных SQLite и PostgreSQL.
Выявляет отсутствующие таблицы и поля, которые нужно перенести при миграции.
"""

import sqlite3
import psycopg2
import os
import sys

# Параметры подключения
SQLITE_DB_PATH = "backend/full_api_new.db"
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "111")
PG_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
PG_DB = os.getenv("POSTGRES_DB", "ofs_db_new")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

def get_sqlite_tables():
    """Получает список таблиц из SQLite базы данных"""
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    except Exception as e:
        print(f"Ошибка при получении таблиц SQLite: {e}")
        sys.exit(1)

def get_sqlite_table_columns(table_name):
    """Получает информацию о столбцах таблицы SQLite"""
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        conn.close()
        return columns
    except Exception as e:
        print(f"Ошибка при получении столбцов SQLite для таблицы {table_name}: {e}")
        return {}

def get_pg_tables():
    """Получает список таблиц из PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=PG_SERVER,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            dbname=PG_DB
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND table_name != 'alembic_version'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    except Exception as e:
        print(f"Ошибка при получении таблиц PostgreSQL: {e}")
        sys.exit(1)

def get_pg_table_columns(table_name):
    """Получает информацию о столбцах таблицы PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=PG_SERVER,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            dbname=PG_DB
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s
        """, (table_name,))
        columns = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return columns
    except Exception as e:
        print(f"Ошибка при получении столбцов PostgreSQL для таблицы {table_name}: {e}")
        return {}

def compare_databases():
    """Сравнивает структуры баз данных SQLite и PostgreSQL"""
    sqlite_tables = get_sqlite_tables()
    pg_tables = get_pg_tables()
    
    print(f"SQLite таблицы ({len(sqlite_tables)}): {', '.join(sqlite_tables)}")
    print(f"PostgreSQL таблицы ({len(pg_tables)}): {', '.join(pg_tables)}")
    
    # Ищем отсутствующие таблицы
    missing_tables = []
    for table in sqlite_tables:
        if table.lower() not in [t.lower() for t in pg_tables]:
            missing_tables.append(table)
    
    if missing_tables:
        print(f"\nВ PostgreSQL отсутствуют {len(missing_tables)} таблиц из SQLite:")
        for table in missing_tables:
            print(f"  - {table}")
        print("\nДетали отсутствующих таблиц:")
        for table in missing_tables:
            columns = get_sqlite_table_columns(table)
            print(f"\n--- {table} ---")
            for column, data_type in columns.items():
                print(f"  {column} ({data_type})")
    else:
        print("\nВсе таблицы из SQLite присутствуют в PostgreSQL (возможно, с другими именами).")
    
    # Проверяем столбцы в общих таблицах
    common_tables = []
    for sqlite_table in sqlite_tables:
        for pg_table in pg_tables:
            if sqlite_table.lower() == pg_table.lower():
                common_tables.append((sqlite_table, pg_table))
                break
    
    print(f"\nПроверка столбцов в {len(common_tables)} общих таблицах:")
    for sqlite_table, pg_table in common_tables:
        sqlite_columns = get_sqlite_table_columns(sqlite_table)
        pg_columns = get_pg_table_columns(pg_table)
        
        missing_columns = []
        for col_name, col_type in sqlite_columns.items():
            if col_name.lower() not in [c.lower() for c in pg_columns.keys()]:
                missing_columns.append((col_name, col_type))
        
        if missing_columns:
            print(f"\n--- Таблица {sqlite_table} (PostgreSQL: {pg_table}) ---")
            print(f"  Отсутствуют {len(missing_columns)} столбцов:")
            for col_name, col_type in missing_columns:
                print(f"    - {col_name} ({col_type})")

if __name__ == "__main__":
    compare_databases() 