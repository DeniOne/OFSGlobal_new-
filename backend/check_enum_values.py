#!/usr/bin/env python
"""
Скрипт для получения значений перечисления orgtype в PostgreSQL
"""
import psycopg2
import sys
import traceback

def main():
    print("\n=== Проверка значений перечисления ===\n")
    
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
        
        cur = conn.cursor()
        
        # Получаем информацию о перечислении orgtype
        print("\nПолучаем информацию о типе orgtype...")
        try:
            cur.execute("""
                SELECT t.typname AS type_name,
                       n.nspname AS schema_name,
                       pg_catalog.format_type(t.oid, NULL) AS display_name
                FROM pg_catalog.pg_type t
                LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typname = 'orgtype'
            """)
            
            type_info = cur.fetchone()
            
            if type_info:
                print(f"Найдено перечисление: {type_info}")
            else:
                print("Перечисление orgtype не найдено!")
        except Exception as e:
            print(f"Ошибка при получении информации о типе: {e}")
            traceback.print_exc()
        
        # Попробуем получить значения напрямую из pg_enum
        print("\nПолучаем значения напрямую из pg_enum...")
        try:
            cur.execute("""
                SELECT e.enumlabel
                FROM pg_enum e
                JOIN pg_type t ON e.enumtypid = t.oid
                WHERE t.typname = 'orgtype'
                ORDER BY e.enumlabel
            """)
            
            values = cur.fetchall()
            
            if values:
                print("Допустимые значения для orgtype:")
                for value in values:
                    print(f"- {value[0]}")
            else:
                print("Значения для orgtype не найдены!")
        except Exception as e:
            print(f"Ошибка при получении значений: {e}")
            traceback.print_exc()
        
        # Проверим доступные типы
        print("\nПолучаем все пользовательские типы в базе данных...")
        try:
            cur.execute("""
                SELECT n.nspname as schema, t.typname as type
                FROM pg_type t
                JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typtype = 'e' -- enumerated type
                ORDER BY schema, type
            """)
            
            types = cur.fetchall()
            
            if types:
                print("Найденные пользовательские типы ENUM:")
                for schema, type_name in types:
                    print(f"- {schema}.{type_name}")
            else:
                print("Пользовательские типы ENUM не найдены!")
        except Exception as e:
            print(f"Ошибка при получении типов: {e}")
            traceback.print_exc()
        
        # Закрываем соединение
        cur.close()
        conn.close()
        print("\nПроверка завершена")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 