#!/usr/bin/env python
"""
Скрипт для проверки допустимых значений перечислений в PostgreSQL
"""
import psycopg2
import sys
import traceback

def main():
    print("\n=== Проверка перечислений PostgreSQL ===\n")
    
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
        
        # Создаем курсор
        cur = conn.cursor()
        
        # Проверяем все типы enum в базе данных
        print("\nПроверяем все типы ENUM в базе данных...")
        cur.execute("""
            SELECT t.typname, e.enumlabel
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid  
            ORDER BY t.typname, e.enumlabel
        """)
        
        enums = cur.fetchall()
        
        if enums:
            current_type = None
            print("Найденные ENUM типы и их значения:")
            
            for enum_type, enum_value in enums:
                if enum_type != current_type:
                    print(f"\n- {enum_type}:")
                    current_type = enum_type
                
                print(f"  * {enum_value}")
        else:
            print("ENUM типы не найдены в базе данных")
        
        # Проверяем структуру таблицы organizations
        print("\nПроверяем структуру таблицы organizations...")
        cur.execute("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = 'organizations'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("Колонки таблицы organizations:")
        for col_name, data_type, udt_name in columns:
            print(f"- {col_name}: {data_type} ({udt_name})")
        
        # Закрываем соединение
        cur.close()
        conn.close()
        print("\nПроверка успешно завершена!")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 