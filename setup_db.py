"""
Скрипт для настройки базы данных с нуля.
Создаёт базу данных, применяет миграции и создаёт начальные данные.
"""
import os
import sys
import time
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import subprocess
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

def create_database():
    """Создаёт базу данных, если она не существует."""
    
    # Подключаемся к PostgreSQL для создания БД
    print(f"[INFO] Подключаемся к PostgreSQL на сервере {DB_PARAMS['host']}...")
    try:
        conn = psycopg2.connect(
            dbname='postgres',  # Подключаемся к системной БД postgres
            user=DB_PARAMS['user'],
            password=DB_PARAMS['password'],
            host=DB_PARAMS['host']
        )
        
        # Устанавливаем автокоммит для создания БД
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Создаем курсор
        with conn.cursor() as cur:
            # Проверяем, существует ли база данных
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_PARAMS['dbname'],))
            exists = cur.fetchone()
            
            if not exists:
                print(f"[INFO] Создаём базу данных {DB_PARAMS['dbname']}...")
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_PARAMS['dbname'])))
                print(f"[SUCCESS] База данных {DB_PARAMS['dbname']} успешно создана!")
            else:
                print(f"[INFO] База данных {DB_PARAMS['dbname']} уже существует.")
        
        # Закрываем соединение с PostgreSQL
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Ошибка при создании базы данных: {e}")
        sys.exit(1)

def run_migrations():
    """Запускает миграции Alembic."""
    
    print("[INFO] Применяем миграции...")
    try:
        # Устанавливаем переменные окружения для миграций
        env = os.environ.copy()
        env["POSTGRES_DB"] = DB_PARAMS['dbname']
        env["POSTGRES_USER"] = DB_PARAMS['user']
        env["POSTGRES_PASSWORD"] = DB_PARAMS['password']
        env["POSTGRES_SERVER"] = DB_PARAMS['host']
        
        # Переходим в директорию backend и запускаем миграции
        os.chdir("backend")
        result = subprocess.run(["alembic", "upgrade", "head"], env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[SUCCESS] Миграции успешно применены!")
            print(result.stdout)
        else:
            print(f"[ERROR] Ошибка при применении миграций: {result.stderr}")
            print("[INFO] Пробуем создать таблицы напрямую через SQLAlchemy...")
            
            # Если миграции не сработали, используем create_tables.py
            create_tables_result = subprocess.run(["python", "create_tables.py"], env=env, capture_output=True, text=True)
            
            if create_tables_result.returncode == 0:
                print("[SUCCESS] Таблицы успешно созданы через SQLAlchemy!")
                print(create_tables_result.stdout)
            else:
                print(f"[ERROR] Ошибка при создании таблиц: {create_tables_result.stderr}")
                sys.exit(1)
        
        # Возвращаемся в корневую директорию
        os.chdir("..")
        
    except Exception as e:
        print(f"[ERROR] Ошибка при выполнении миграций: {e}")
        sys.exit(1)

def create_initial_data():
    """Создаёт начальные данные в БД."""
    
    print("[INFO] Создаём начальные данные...")
    try:
        # Подключаемся к созданной БД
        conn = psycopg2.connect(
            dbname=DB_PARAMS['dbname'],
            user=DB_PARAMS['user'],
            password=DB_PARAMS['password'],
            host=DB_PARAMS['host']
        )
        
        # Создаем курсор
        with conn.cursor() as cur:
            # Проверяем, есть ли уже данные в таблице organization
            cur.execute("SELECT COUNT(*) FROM organization")
            count = cur.fetchone()[0]
            
            if count == 0:
                # Создаем тестовую организацию
                cur.execute("""
                    INSERT INTO organization (name, legal_name, org_type, is_active, created_at, updated_at)
                    VALUES ('ОФС Глобал', 'ООО "ОФС Глобал"', 'company', TRUE, NOW(), NOW())
                    RETURNING id
                """)
                organization_id = cur.fetchone()[0]
                
                # Создаем корневое подразделение
                cur.execute("""
                    INSERT INTO division (name, organization_id, code, is_active, created_at, updated_at)
                    VALUES ('Главный офис', %s, 'HQ', TRUE, NOW(), NOW())
                    RETURNING id
                """, (organization_id,))
                division_id = cur.fetchone()[0]
                
                # Создаем должность директора
                cur.execute("""
                    INSERT INTO position (name, description, is_active, created_at, updated_at)
                    VALUES ('Генеральный директор', 'Руководитель организации', TRUE, NOW(), NOW())
                    RETURNING id
                """)
                position_id = cur.fetchone()[0]
                
                print(f"[SUCCESS] Начальные данные успешно созданы!")
            else:
                print(f"[INFO] В базе данных уже есть организации, пропускаем создание начальных данных.")
        
        # Фиксируем изменения
        conn.commit()
        
        # Закрываем соединение
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Ошибка при создании начальных данных: {e}")
        sys.exit(1)

def update_env_files():
    """Обновляет файлы .env для соответствия настроек."""
    
    try:
        # Создаем основной .env файл (если не существует)
        if not os.path.exists(".env"):
            with open(".env", "w") as f:
                f.write(f"DB_NAME={DB_PARAMS['dbname']}\n")
                f.write(f"DB_USER={DB_PARAMS['user']}\n")
                f.write(f"DB_PASSWORD={DB_PARAMS['password']}\n")
                f.write(f"DB_HOST={DB_PARAMS['host']}\n")
            print("[SUCCESS] Создан файл .env")
        
        # Создаем .env файл для backend (если не существует)
        if not os.path.exists("backend/.env"):
            with open("backend/.env", "w") as f:
                f.write(f"POSTGRES_DB={DB_PARAMS['dbname']}\n")
                f.write(f"POSTGRES_USER={DB_PARAMS['user']}\n")
                f.write(f"POSTGRES_PASSWORD={DB_PARAMS['password']}\n")
                f.write(f"POSTGRES_SERVER={DB_PARAMS['host']}\n")
                f.write(f"POSTGRES_PORT=5432\n")
            print("[SUCCESS] Создан файл backend/.env")
        
        print("[SUCCESS] Файлы окружения обновлены!")
        
    except Exception as e:
        print(f"[ERROR] Ошибка при обновлении файлов окружения: {e}")
        sys.exit(1)

def main():
    """Основная функция для настройки БД."""
    
    print("[START] Начинаем настройку базы данных...")
    
    # Обновляем файлы .env
    update_env_files()
    
    # Создаем базу данных
    create_database()
    
    # Даем время PostgreSQL на подготовку БД
    time.sleep(1)
    
    # Запускаем миграции
    run_migrations()
    
    # Создаем начальные данные
    create_initial_data()
    
    print("\n[SUCCESS] Настройка базы данных успешно завершена!")
    print(f"[INFO] База данных {DB_PARAMS['dbname']} готова к использованию.")

if __name__ == "__main__":
    main() 