#!/usr/bin/env python
"""
Скрипт для тестирования проблем с кодировкой в PostgreSQL
"""
import psycopg2
import sys
import traceback

def main():
    print("\n=== Тест кодировки PostgreSQL ===\n")
    
    # Параметры подключения
    conn_params = {
        'dbname': 'ofs_db_new',
        'user': 'postgres',
        'password': '111',  
        'host': 'localhost',
        'client_encoding': 'utf8'
    }
    
    try:
        # Подключаемся к PostgreSQL
        print("Подключаемся к PostgreSQL...")
        conn = psycopg2.connect(**conn_params)
        print("Подключение успешно!")
        
        # Проверяем кодировку
        cur = conn.cursor()
        cur.execute("SHOW client_encoding;")
        client_encoding = cur.fetchone()[0]
        print(f"Кодировка клиента: {client_encoding}")
        
        cur.execute("SHOW server_encoding;")
        server_encoding = cur.fetchone()[0]
        print(f"Кодировка сервера: {server_encoding}")
        
        # Проверяем существующие таблицы
        print("\nПроверяем существующие таблицы...")
        cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        tables = cur.fetchall()
        if tables:
            print("Существующие таблицы:")
            for table in tables:
                print(f"- {table[0]}")
        else:
            print("В базе нет таблиц в схеме public")
        
        # Создаем тестовую таблицу
        print("\nСоздаем тестовую таблицу test_encoding...")
        try:
            cur.execute("DROP TABLE IF EXISTS test_encoding")
            cur.execute("""
                CREATE TABLE test_encoding (
                    id SERIAL PRIMARY KEY,
                    simple_text VARCHAR(100),
                    russian_text VARCHAR(100),
                    special_chars VARCHAR(100)
                )
            """)
            conn.commit()
            print("Таблица успешно создана")
            
            # Вставляем тестовые данные
            print("\nВставляем тестовые данные...")
            cur.execute("""
                INSERT INTO test_encoding (simple_text, russian_text, special_chars)
                VALUES 
                    ('Simple ASCII text', 'Русский текст', 'Special chars: !@#$%^&*()_+'),
                    ('Another text', 'Еще один текст', 'More symbols: €£¥©®™')
            """)
            conn.commit()
            print("Данные успешно вставлены")
            
            # Читаем данные
            print("\nЧитаем данные из тестовой таблицы...")
            cur.execute("SELECT * FROM test_encoding")
            rows = cur.fetchall()
            for row in rows:
                print(f"Row: {row}")
                
        except Exception as e:
            print(f"Ошибка с тестовой таблицей: {e}")
            traceback.print_exc()
            conn.rollback()
        
        # Проверяем таблицу организаций
        print("\nПроверяем таблицу organizations...")
        try:
            cur.execute("SELECT COUNT(*) FROM organizations")
            count = cur.fetchone()[0]
            print(f"В таблице organizations {count} записей")
            
            if count > 0:
                print("Первые 3 записи:")
                cur.execute("SELECT id, name, code, org_type FROM organizations LIMIT 3")
                rows = cur.fetchall()
                for row in rows:
                    print(f"- {row}")
        except Exception as e:
            print(f"Ошибка при проверке таблицы organizations: {e}")
            traceback.print_exc()
        
        # Закрываем соединение
        cur.close()
        conn.close()
        print("\nТестирование успешно завершено")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())