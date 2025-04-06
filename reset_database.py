"""
Скрипт для полного сброса и пересоздания базы данных.
ВНИМАНИЕ: Этот скрипт удалит все данные в базе!
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

def reset_database():
    """Удаляет и создает заново базу данных."""
    
    # Подключаемся к PostgreSQL
    print(f"[INFO] Подключаемся к PostgreSQL на сервере {DB_PARAMS['host']}...")
    try:
        conn = psycopg2.connect(
            dbname='postgres',  # Подключаемся к системной БД postgres
            user=DB_PARAMS['user'],
            password=DB_PARAMS['password'],
            host=DB_PARAMS['host']
        )
        
        # Устанавливаем автокоммит для создания/удаления БД
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Создаем курсор
        with conn.cursor() as cur:
            # Проверяем существует ли база данных
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_PARAMS['dbname'],))
            exists = cur.fetchone()
            
            if exists:
                print(f"[INFO] Отключаем активные подключения к БД {DB_PARAMS['dbname']}...")
                cur.execute(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{DB_PARAMS['dbname']}'
                    AND pid <> pg_backend_pid()
                """)
                
                print(f"[INFO] Удаляем базу данных {DB_PARAMS['dbname']}...")
                cur.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(DB_PARAMS['dbname'])))
                print(f"[SUCCESS] База данных {DB_PARAMS['dbname']} успешно удалена!")
            
            # Создаем базу данных заново
            print(f"[INFO] Создаем базу данных {DB_PARAMS['dbname']}...")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_PARAMS['dbname'])))
            print(f"[SUCCESS] База данных {DB_PARAMS['dbname']} успешно создана!")
        
        # Закрываем соединение с PostgreSQL
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Ошибка при пересоздании базы данных: {e}")
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
        
        # Проверяем наличие миграций
        has_migrations = os.path.exists("alembic/versions")
        
        if has_migrations:
            # Выполняем миграции
            result = subprocess.run(["alembic", "upgrade", "head"], env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("[SUCCESS] Миграции успешно применены!")
                print(result.stdout)
            else:
                print(f"[ERROR] Ошибка при применении миграций: {result.stderr}")
                sys.exit(1)
        else:
            print("[WARNING] Миграции не найдены. Продолжаем...")
        
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
            # Создаем таблицу organization, если еще не существует
            cur.execute("""
                CREATE TABLE IF NOT EXISTS organization (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    legal_name VARCHAR(255),
                    description TEXT,
                    code VARCHAR(50),
                    org_type VARCHAR(50) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    ckp VARCHAR(500)
                )
            """)
            
            # Создаем тестовую организацию
            cur.execute("""
                INSERT INTO organization (name, legal_name, org_type, is_active, created_at, updated_at)
                VALUES ('ОФС Глобал', 'ООО "ОФС Глобал"', 'company', TRUE, NOW(), NOW())
                RETURNING id
            """)
            organization_id = cur.fetchone()[0]
            
            # Создаем таблицу division
            cur.execute("""
                CREATE TABLE IF NOT EXISTS division (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    organization_id INTEGER REFERENCES organization(id),
                    parent_id INTEGER REFERENCES division(id),
                    code VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    ckp VARCHAR(500)
                )
            """)
            
            # Создаем корневое подразделение
            cur.execute("""
                INSERT INTO division (name, organization_id, code, is_active, created_at, updated_at)
                VALUES ('Главный офис', %s, 'HQ', TRUE, NOW(), NOW())
                RETURNING id
            """, (organization_id,))
            division_id = cur.fetchone()[0]
            
            # Создаем таблицу position
            cur.execute("""
                CREATE TABLE IF NOT EXISTS position (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Создаем должность директора
            cur.execute("""
                INSERT INTO position (name, description, is_active, created_at, updated_at)
                VALUES ('Генеральный директор', 'Руководитель организации', TRUE, NOW(), NOW())
                RETURNING id
            """)
            position_id = cur.fetchone()[0]
            
            # Создаем таблицу staff
            cur.execute("""
                CREATE TABLE IF NOT EXISTS staff (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    position VARCHAR(255) NOT NULL,
                    division VARCHAR(255) NOT NULL,
                    level INTEGER NOT NULL DEFAULT 0,
                    organization_id INTEGER REFERENCES organization(id) NOT NULL,
                    parent_id INTEGER REFERENCES staff(id),
                    legal_entity_id INTEGER REFERENCES organization(id),
                    location_id INTEGER REFERENCES organization(id),
                    photo_path VARCHAR(255),
                    phone VARCHAR(20),
                    email VARCHAR(255) UNIQUE,
                    telegram_id VARCHAR(255),
                    registration_address TEXT,
                    actual_address TEXT,
                    passport_path VARCHAR(255),
                    work_contract_path VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Создаем таблицу функциональных отношений
            cur.execute("""
                CREATE TABLE IF NOT EXISTS functional_relation (
                    id SERIAL PRIMARY KEY,
                    manager_id INTEGER REFERENCES staff(id) NOT NULL,
                    subordinate_id INTEGER REFERENCES staff(id) NOT NULL,
                    relation_type VARCHAR(50),
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Создаем таблицу sections (отделы)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS section (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    division_id INTEGER REFERENCES division(id),
                    code VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    ckp VARCHAR(500)
                )
            """)
            
            # Создаем таблицу functions (функции)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS function (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    section_id INTEGER REFERENCES section(id),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    ckp VARCHAR(500)
                )
            """)
            
            # Создаем таблицу staff_function
            cur.execute("""
                CREATE TABLE IF NOT EXISTS staff_function (
                    id SERIAL PRIMARY KEY,
                    staff_id INTEGER REFERENCES staff(id) NOT NULL,
                    function_id INTEGER REFERENCES function(id) NOT NULL,
                    is_primary BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            print(f"[SUCCESS] Начальные данные и структура БД успешно созданы!")
        
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
        # Создаем .env файл для backend если не существует
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
    """Основная функция для пересоздания БД."""
    
    # Спрашиваем пользователя о подтверждении
    print("[WARNING] ВНИМАНИЕ! Этот скрипт полностью удалит и создаст заново базу данных!")
    confirm = input("Вы уверены, что хотите продолжить? (y/n): ")
    
    if confirm.lower() != 'y':
        print("[INFO] Операция отменена.")
        return
    
    print("[START] Начинаем пересоздание базы данных...")
    
    # Обновляем файлы .env
    update_env_files()
    
    # Пересоздаем базу данных
    reset_database()
    
    # Даем время PostgreSQL на подготовку БД
    time.sleep(1)
    
    # Создаем начальные данные
    create_initial_data()
    
    # Запускаем миграции
    # run_migrations()  # Закомментировано, так как мы создаем структуру вручную
    
    print("\n[SUCCESS] База данных успешно пересоздана!")
    print(f"[INFO] База данных {DB_PARAMS['dbname']} готова к использованию.")

if __name__ == "__main__":
    main() 