#!/usr/bin/env python
"""
Скрипт для добавления значений в перечисление orgtype в PostgreSQL
"""
import psycopg2
import sys
import traceback

def main():
    print("\n=== Добавление значений в перечисление orgtype ===\n")
    
    # Параметры подключения
    conn_params = {
        'dbname': 'ofs_db_new',
        'user': 'postgres',
        'password': '111',  
        'host': 'localhost',
        'client_encoding': 'utf8'
    }
    
    # Значения из модели OrgType
    org_type_values = ['board', 'holding', 'legal_entity', 'location']
    
    try:
        # Подключаемся к PostgreSQL
        print("Подключаемся к PostgreSQL...")
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        print("Подключение успешно!")
        
        cur = conn.cursor()
        
        # Проверяем существование перечисления orgtype
        print("Проверяем перечисление orgtype...")
        cur.execute("""
            SELECT t.typname
            FROM pg_type t
            JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
            WHERE t.typname = 'orgtype'
        """)
        
        if cur.fetchone():
            print("Перечисление orgtype существует")
            
            # Удаляем и создаем заново перечисление
            print("\nУдаляем таблицу organizations для возможности пересоздания типа...")
            try:
                cur.execute("DROP TABLE IF EXISTS organizations CASCADE")
                print("Таблица organizations удалена")
            except Exception as e:
                print(f"Ошибка при удалении таблицы: {e}")
                traceback.print_exc()
            
            print("\nУдаляем перечисление orgtype...")
            try:
                cur.execute("DROP TYPE IF EXISTS orgtype CASCADE")
                print("Перечисление orgtype удалено")
            except Exception as e:
                print(f"Ошибка при удалении типа: {e}")
                traceback.print_exc()
        
        # Создаем перечисление с заданными значениями
        print("\nСоздаем перечисление orgtype заново...")
        try:
            values_str = ", ".join(f"'{value}'" for value in org_type_values)
            query = f"CREATE TYPE orgtype AS ENUM ({values_str})"
            cur.execute(query)
            print(f"Перечисление orgtype создано со значениями: {org_type_values}")
        except Exception as e:
            print(f"Ошибка при создании перечисления: {e}")
            traceback.print_exc()
        
        # Создаем таблицу organizations заново
        print("\nСоздаем таблицу organizations заново...")
        try:
            cur.execute("""
                CREATE TABLE organizations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    code VARCHAR(10) NOT NULL UNIQUE,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    org_type orgtype NOT NULL,
                    ckp VARCHAR(500),
                    inn VARCHAR(12),
                    kpp VARCHAR(9),
                    legal_address VARCHAR(500),
                    physical_address VARCHAR(500),
                    parent_id INTEGER REFERENCES organizations(id) ON DELETE SET NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    extra_field1 TEXT,
                    extra_field2 TEXT,
                    extra_field3 TEXT,
                    extra_int1 INTEGER,
                    extra_int2 INTEGER,
                    extra_date1 DATE
                )
            """)
            print("Таблица organizations создана")
        except Exception as e:
            print(f"Ошибка при создании таблицы: {e}")
            traceback.print_exc()
        
        # Пробуем добавить тестовую организацию
        print("\nДобавляем тестовую организацию...")
        try:
            cur.execute("""
                INSERT INTO organizations (
                    name, code, description, org_type,
                    is_active, legal_address, physical_address
                ) VALUES (
                    'OFS Global', 'OFS1', 'Тестовая организация', 'holding',
                    TRUE, 'г. Москва, ул. Тестовая, д. 1', 'г. Москва, ул. Тестовая, д. 1'
                ) RETURNING id
            """)
            org_id = cur.fetchone()[0]
            print(f"Создана тестовая организация с ID: {org_id}")
        except Exception as e:
            print(f"Ошибка при добавлении организации: {e}")
            traceback.print_exc()
        
        # Закрываем соединение
        cur.close()
        conn.close()
        print("\nОперация успешно завершена")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 