import psycopg2
import os

# Параметры подключения
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "111")
PG_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
PG_DB = os.getenv("POSTGRES_DB", "ofs_db_new")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

# Подключение к PostgreSQL
try:
    connection_string = f"host={PG_SERVER} port={PG_PORT} user={PG_USER} password={PG_PASSWORD} dbname={PG_DB}"
    conn = psycopg2.connect(connection_string)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Получаем список всех таблиц
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
    """)
    tables = cursor.fetchall()
    
    if not tables:
        print("В базе данных нет таблиц для удаления.")
    else:
        # Отключаем проверку внешних ключей
        cursor.execute("SET session_replication_role TO 'replica';")
        
        # Удаляем все таблицы
        print("Удаляем таблицы:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;')
        
        # Восстанавливаем проверку внешних ключей
        cursor.execute("SET session_replication_role TO 'origin';")
        
        print("Все таблицы успешно удалены.")
    
    # Удаляем последовательности
    cursor.execute("""
        SELECT sequence_name FROM information_schema.sequences
        WHERE sequence_schema = 'public'
    """)
    sequences = cursor.fetchall()
    
    if sequences:
        print("Удаляем последовательности:")
        for seq in sequences:
            seq_name = seq[0]
            print(f"  - {seq_name}")
            cursor.execute(f'DROP SEQUENCE IF EXISTS "{seq_name}" CASCADE;')
        
        print("Все последовательности успешно удалены.")
    
    # Удаляем типы данных пользователя (enums)
    cursor.execute("""
        SELECT typname FROM pg_type JOIN pg_catalog.pg_namespace n ON n.oid = pg_type.typnamespace
        WHERE typtype = 'e' AND nspname = 'public';
    """)
    types = cursor.fetchall()
    
    if types:
        print("Удаляем пользовательские типы данных (enums):")
        for t in types:
            type_name = t[0]
            print(f"  - {type_name}")
            cursor.execute(f'DROP TYPE IF EXISTS "{type_name}" CASCADE;')
        
        print("Все типы данных успешно удалены.")
    
    # Удаляем запись из alembic_version
    cursor.execute("""
        DROP TABLE IF EXISTS alembic_version;
    """)
    print("Таблица alembic_version удалена.")
    
    cursor.close()
    conn.close()
    print("База данных очищена и готова для новой миграции.")
    
except Exception as e:
    print(f"Ошибка при работе с PostgreSQL: {str(e)}")
    print("Проверьте настройки подключения и убедитесь, что сервер запущен.") 