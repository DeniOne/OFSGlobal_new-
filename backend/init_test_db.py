import os
import sys
import sqlite3
from datetime import datetime
from passlib.context import CryptContext
import bcrypt  # Импортируем bcrypt

# Определяем путь к базе данных
DATABASE_PATH = 'full_api_new.db'  # <-- Используем ту же базу, что и в auth_api.py

# Настройки хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def init_db():
    """Инициализирует тестовую базу данных"""
    print("[LOG] Начинаю инициализацию тестовой базы данных...")
    
    # Проверяем существование файла БД и удаляем его если нужно пересоздать
    if os.path.exists(DATABASE_PATH):
        print(f"[LOG] База данных {DATABASE_PATH} уже существует, удаляем и создаем заново")
        os.remove(DATABASE_PATH)
    
    # Создаем соединение с базой данных
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("[LOG] Создаю таблицы...")
    
    # Создаем таблицу пользователей
    cursor.execute('''
    CREATE TABLE user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        email TEXT NOT NULL UNIQUE,
        hashed_password TEXT NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        is_superuser BOOLEAN NOT NULL DEFAULT 0
    )
    ''')
    
    # Создаем таблицу организаций
    cursor.execute('''
    CREATE TABLE organization (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        code TEXT,
        org_type TEXT NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
    ''')
    
    # Создаем таблицу подразделений
    cursor.execute('''
    CREATE TABLE division (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        code TEXT,
        organization_id INTEGER,
        parent_id INTEGER,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (organization_id) REFERENCES organization (id),
        FOREIGN KEY (parent_id) REFERENCES division (id)
    )
    ''')
    
    # Создаем таблицу должностей
    cursor.execute('''
    CREATE TABLE position (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
    ''')
    
    # Создаем таблицу сотрудников
    cursor.execute('''
    CREATE TABLE staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        division_id INTEGER,
        position_id INTEGER,
        organization_id INTEGER,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (division_id) REFERENCES division (id),
        FOREIGN KEY (position_id) REFERENCES position (id),
        FOREIGN KEY (organization_id) REFERENCES organization (id)
    )
    ''')
    
    print("[LOG] Таблицы созданы.")
    print("[LOG] Создаю суперпользователя...")
    
    # Хешируем пароль для суперпользователя
    hashed_password = get_password_hash("admin")
    
    # Добавляем суперпользователя
    cursor.execute('''
    INSERT INTO user (full_name, email, hashed_password, is_active, is_superuser)
    VALUES (?, ?, ?, ?, ?)
    ''', ("Admin User", "admin@ofs-global.com", hashed_password, True, True))
    
    print("[LOG] Создаю тестовые данные...")
    
    # Добавляем тестовую организацию
    now = datetime.now().isoformat()
    cursor.execute('''
    INSERT INTO organization (name, description, code, org_type, is_active, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ("ОФС Глобал", "Тестовая организация", "OFS", "HOLDING", True, now, now))
    
    # Получаем ID организации
    cursor.execute("SELECT last_insert_rowid()")
    organization_id = cursor.fetchone()[0]
    
    # Добавляем корневое подразделение
    cursor.execute('''
    INSERT INTO division (name, description, code, organization_id, is_active, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ("Главный офис", "Корневое подразделение", "HQ", organization_id, True, now, now))
    
    # Получаем ID подразделения
    cursor.execute("SELECT last_insert_rowid()")
    division_id = cursor.fetchone()[0]
    
    # Добавляем должность
    cursor.execute('''
    INSERT INTO position (name, description, is_active, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?)
    ''', ("Генеральный директор", "Руководитель организации", True, now, now))
    
    # Получаем ID должности
    cursor.execute("SELECT last_insert_rowid()")
    position_id = cursor.fetchone()[0]
    
    # Добавляем сотрудника
    cursor.execute('''
    INSERT INTO staff (full_name, phone, email, division_id, position_id, organization_id, is_active, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ("Иванов Иван Иванович", "+7 (999) 123-45-67", "ivanov@example.com", division_id, position_id, organization_id, True, now, now))
    
    # Сохраняем изменения
    conn.commit()
    
    print("[LOG] Тестовая база данных инициализирована успешно.")
    print(f"[LOG] Создан суперпользователь: admin@ofs-global.com / admin")
    print(f"[LOG] База данных сохранена: {os.path.abspath(DATABASE_PATH)}")

if __name__ == "__main__":
    init_db() 