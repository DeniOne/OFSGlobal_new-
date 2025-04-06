"""
Скрипт для добавления тестовых данных в базу данных.
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

def add_test_data():
    """Добавляет тестовые данные в базу данных."""
    
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
        
        # Добавляем организацию
        print("📝 Добавляем организацию 'ФОТОМАТРИЦА'...")
        cur.execute("""
            INSERT INTO organizations (name, legal_name, description, code, org_type, is_active, ckp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, ('ФОТОМАТРИЦА', 'ООО "ФОТОМАТРИЦА"', 'Компания по производству фототехники', 'FM-001', 
              'COMMERCIAL', True, 'Производство высококачественной фототехники'))
        
        org_id = cur.fetchone()[0]
        print(f"✅ Организация создана с ID: {org_id}")
        
        # Добавляем подразделение
        print("📝 Добавляем подразделение 'Департамент разработки'...")
        cur.execute("""
            INSERT INTO divisions (name, organization_id, code, is_active, ckp)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, ('Департамент разработки', org_id, 'DIV-DEV', True, 'Разработка новых моделей фототехники'))
        
        div_id = cur.fetchone()[0]
        print(f"✅ Подразделение создано с ID: {div_id}")
        
        # Добавляем отдел
        print("📝 Добавляем отдел 'Отдел фотокамер'...")
        cur.execute("""
            INSERT INTO sections (name, division_id, code, is_active, ckp)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, ('Отдел фотокамер', div_id, 'SEC-CAM', True, 'Разработка инновационных фотокамер'))
        
        sec_id = cur.fetchone()[0]
        print(f"✅ Отдел создан с ID: {sec_id}")
        
        # Добавляем функцию
        print("📝 Добавляем функцию 'Функция дизайна фотокамер'...")
        cur.execute("""
            INSERT INTO functions (name, section_id, is_active, ckp)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, ('Функция дизайна фотокамер', sec_id, True, 'Разработка эргономичных и стильных корпусов'))
        
        func_id = cur.fetchone()[0]
        print(f"✅ Функция создана с ID: {func_id}")
        
        # Должность
        print("📝 Добавляем должность 'Ведущий дизайнер'...")
        cur.execute("""
            INSERT INTO positions (name, description, is_active)
            VALUES (%s, %s, %s)
            RETURNING id
        """, ('Ведущий дизайнер', 'Ведущий специалист по дизайну продукции', True))
        
        pos_id = cur.fetchone()[0]
        print(f"✅ Должность создана с ID: {pos_id}")
        
        # Фиксируем изменения
        conn.commit()
        
        # Закрываем соединение
        cur.close()
        conn.close()
        
        print("\n✅ Тестовые данные успешно добавлены!")
        
    except Exception as e:
        print(f"❌ Ошибка при добавлении тестовых данных: {e}")
        if 'conn' in locals():
            conn.rollback()

if __name__ == "__main__":
    add_test_data() 