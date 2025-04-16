import psycopg2
import os
from urllib.parse import quote_plus

# Параметры подключения
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "111")
PG_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
PG_DB = os.getenv("POSTGRES_DB", "ofs_db_new")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

# Пробуем подключиться к серверу PostgreSQL
try:
    # Создаем строку подключения с экранированием пароля
    connection_string = f"host={PG_SERVER} port={PG_PORT} user={PG_USER} password={PG_PASSWORD} dbname=postgres"
    
    # Сначала пробуем подключиться к системной базе postgres
    print(f"Попытка подключения к PostgreSQL серверу...")
    conn = psycopg2.connect(connection_string)
    conn.autocommit = True  # Сразу включаем автокоммит
    cursor = conn.cursor()
    
    # Проверяем, существует ли уже наша база данных
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (PG_DB,))
    exists = cursor.fetchone()
    
    if exists:
        print(f"База данных '{PG_DB}' уже существует.")
    else:
        print(f"База данных '{PG_DB}' не существует. Создаем...")
        
        # Создаем базу данных (если её нет)
        cursor.execute(f"CREATE DATABASE {PG_DB}")
        print(f"База данных '{PG_DB}' успешно создана.")
    
    cursor.close()
    conn.close()
    
    # Теперь подключаемся к нашей базе данных
    connection_string = f"host={PG_SERVER} port={PG_PORT} user={PG_USER} password={PG_PASSWORD} dbname={PG_DB}"
    conn = psycopg2.connect(connection_string)
    conn.autocommit = True  # Автокоммит и для второго соединения
    cursor = conn.cursor()
    
    # Проверяем, есть ли таблицы в базе данных
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public'
    """)
    tables = cursor.fetchall()
    
    if tables:
        print("Существующие таблицы в PostgreSQL:")
        for table in tables:
            print(f"- {table[0]}")
    else:
        print("В базе данных пока нет таблиц.")
    
    cursor.close()
    conn.close()
    
    print("Подключение к PostgreSQL успешно!")
except Exception as e:
    print(f"Ошибка при подключении к PostgreSQL: {str(e)}")
    print("Проверьте, запущен ли сервер PostgreSQL и правильны ли настройки подключения.") 