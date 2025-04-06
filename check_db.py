"""
Скрипт для проверки таблиц в базе данных.
"""
import os
import psycopg2
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Параметры подключения к БД
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'ofs_db_new'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost')
}

def check_tables():
    """Проверяет список таблиц в базе данных."""
    
    # Подключаемся к БД
    print(f"🔄 Подключаемся к базе данных {DB_PARAMS['dbname']}...")
    try:
        conn = psycopg2.connect(
            dbname=DB_PARAMS['dbname'],
            user=DB_PARAMS['user'],
            password=DB_PARAMS['password'],
            host=DB_PARAMS['host']
        )
        
        # Создаем курсор
        cur = conn.cursor()
        
        # Получаем список таблиц
        cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public' ORDER BY tablename")
        tables = cur.fetchall()
        
        # Проверка на наличие таблиц
        if not tables:
            print("❌ Таблицы не найдены в базе данных!")
            return
            
        print("\n📊 Статистика по таблицам в базе данных:")
        for table in tables:
            table_name = table[0]
            
            # Получаем количество записей
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            
            print(f"\n🔹 Таблица: {table_name}")
            print(f"  Записей: {count}")
            
            # Если есть записи, показываем пример данных
            if count > 0:
                cur.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cur.fetchall()
                
                # Получаем имена колонок
                cur.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' 
                    ORDER BY ordinal_position
                """)
                columns = [col[0] for col in cur.fetchall()]
                
                print("  Пример данных:")
                for row in rows:
                    print(f"    {dict(zip(columns, row))}")
        
        # Закрываем соединение
        cur.close()
        conn.close()
        
        print("\n✅ Проверка завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при проверке таблиц: {e}")

if __name__ == "__main__":
    check_tables() 