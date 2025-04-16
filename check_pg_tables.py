import psycopg2
import os

# Параметры подключения
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "111")
PG_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
PG_DB = os.getenv("POSTGRES_DB", "ofs_db_new")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

# Пробуем подключиться к PostgreSQL
try:
    # Создаем строку подключения
    connection_string = f"host={PG_SERVER} port={PG_PORT} user={PG_USER} password={PG_PASSWORD} dbname={PG_DB}"
    conn = psycopg2.connect(connection_string)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Получаем список таблиц
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
    """)
    tables = cursor.fetchall()
    
    print(f"Найдено {len(tables)} таблиц в PostgreSQL:")
    
    # Для каждой таблицы проверяем структуру и количество записей
    for table in tables:
        table_name = table[0]
        print(f"\n- Таблица: {table_name}")
        
        # Получаем структуру таблицы
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        columns = cursor.fetchall()
        
        print(f"  Колонки:")
        for col in columns[:5]:  # Первые 5 колонок для краткости
            print(f"  - {col[0]} ({col[1]})")
        
        if len(columns) > 5:
            print(f"    ... и еще {len(columns) - 5} колонок")
        
        # Подсчитываем количество записей
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  Количество записей: {count}")
        
        # Если есть записи, выводим первую запись
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            row = cursor.fetchone()
            if row:
                print(f"  Пример записи:")
                for i, col in enumerate(columns):
                    if i < len(row) and i < 5:  # Первые 5 полей для краткости
                        print(f"    {col[0]}: {row[i]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Ошибка при работе с PostgreSQL: {str(e)}")
    print("Проверьте настройки подключения и убедитесь, что сервер запущен.") 