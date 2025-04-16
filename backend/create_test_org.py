#!/usr/bin/env python
"""
Скрипт для добавления тестовой организации в базу данных PostgreSQL
"""
import psycopg2
import sys
import traceback
from datetime import datetime

def main():
    print("\n=== Создание тестовой организации ===\n")
    
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
        conn.autocommit = True  # Включаем автокоммит
        print("Подключение успешно!")
        
        # Создаем курсор
        cur = conn.cursor()
        
        # Проверяем существующие записи в таблице organizations
        print("\nПроверяем существующие организации...")
        cur.execute("SELECT COUNT(*) FROM organizations")
        count = cur.fetchone()[0]
        print(f"В таблице organizations {count} записей")
        
        if count > 0:
            print("Организации уже существуют, удаляем...")
            cur.execute("DELETE FROM organizations")
            print("Все организации удалены")
        
        # Добавляем тестовую организацию
        print("\nСоздаем тестовую организацию...")
        
        now = datetime.now().isoformat()
        
        # Вставляем организацию
        cur.execute("""
            INSERT INTO organizations (
                name, code, description, org_type, 
                is_active, legal_address, physical_address, 
                created_at, updated_at
            ) VALUES (
                'OFS Global', 'OFS1', 'Тестовая организация для проверки API', 'holding',
                true, 'г. Москва, ул. Тестовая, д. 1', 'г. Москва, ул. Тестовая, д. 1',
                %s, %s
            ) RETURNING id
        """, (now, now))
        
        org_id = cur.fetchone()[0]
        print(f"Создана организация с ID: {org_id}")
        
        # Закрываем соединение
        cur.close()
        conn.close()
        print("\nОрганизация успешно создана!")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 