"""
Скрипт для просмотра статистики базы данных.
"""
import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from prettytable import PrettyTable

# Загрузка переменных окружения
load_dotenv()

# Параметры подключения к БД
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'ofs_db_new'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost')
}

def format_value(value):
    """Форматирует значение для вывода"""
    if value is None:
        return 'NULL'
    if isinstance(value, str) and len(value) > 30:
        return value[:27] + '...'
    return value

def show_db_statistics():
    """Показывает статистику базы данных."""
    
    # Подключаемся к БД
    print(f"🔄 Подключаемся к базе данных {DB_PARAMS['dbname']}...")
    try:
        conn = psycopg2.connect(
            dbname=DB_PARAMS['dbname'],
            user=DB_PARAMS['user'],
            password=DB_PARAMS['password'],
            host=DB_PARAMS['host']
        )
        
        # Создаем курсор, который возвращает словари
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Получаем список всех таблиц
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        
        # Статистика по таблицам
        table_stats = PrettyTable()
        table_stats.field_names = ["Таблица", "Кол-во записей"]
        table_stats.align = "l"
        
        total_records = 0
        table_counts = {}
        
        for table_row in tables:
            table_name = table_row['table_name']
            
            # Получаем количество записей
            cur.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cur.fetchone()['count']
            total_records += count
            table_counts[table_name] = count
            
            # Добавляем в таблицу
            table_stats.add_row([table_name, count])
        
        # Выводим статистику
        print("\n📊 Общая статистика базы данных:")
        print(f"- Всего таблиц: {len(tables)}")
        print(f"- Всего записей: {total_records}")
        print(f"\n{table_stats}")
        
        # Выводим содержимое таблиц с данными
        for table_name, count in table_counts.items():
            if count > 0:
                print(f"\n🔍 Данные в таблице '{table_name}':")
                
                # Получаем записи
                cur.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cur.fetchall()
                
                # Создаем таблицу для вывода
                data_table = PrettyTable()
                data_table.field_names = [col for col in rows[0].keys()]
                data_table.max_width = 30
                
                # Добавляем строки
                for row in rows:
                    data_table.add_row([format_value(row[col]) for col in data_table.field_names])
                
                print(data_table)
                
                if count > 5:
                    print(f"... и еще {count - 5} записей")
        
        # Закрываем соединение
        cur.close()
        conn.close()
        
        print("\n✅ Проверка завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при проверке базы данных: {e}")

if __name__ == "__main__":
    show_db_statistics() 