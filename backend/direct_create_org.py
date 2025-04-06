import sqlite3
import os
import traceback

try:
    # Имя нашей тестовой базы данных
    DB_PATH = "test_direct.db"

    # Удаляем базу, если она существует
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Удалена старая база данных: {DB_PATH}")

    # Создаем соединение
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print(f"Создано соединение с базой данных: {DB_PATH}")

    # Создаем таблицу организаций напрямую через SQL
    cursor.execute('''
    CREATE TABLE organizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        code TEXT NOT NULL UNIQUE,
        description TEXT,
        is_active INTEGER DEFAULT 1,
        org_type TEXT NOT NULL CHECK(org_type IN ('holding', 'legal_entity', 'location')),
        ckp TEXT,
        inn TEXT,
        kpp TEXT,
        legal_address TEXT,
        physical_address TEXT,
        parent_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_id) REFERENCES organizations(id) ON DELETE SET NULL
    );
    ''')
    print("Создана таблица organizations")

    # Создаем индексы
    cursor.execute('CREATE INDEX idx_organizations_name ON organizations(name);')
    cursor.execute('CREATE INDEX idx_organizations_org_type ON organizations(org_type);')
    cursor.execute('CREATE INDEX idx_organizations_parent_id ON organizations(parent_id);')
    print("Созданы индексы для таблицы")

    # Добавляем организацию
    cursor.execute('''
    INSERT INTO organizations (
        name, code, description, is_active, org_type
    ) VALUES (
        ?, ?, ?, ?, ?
    )
    ''', ('ОФС Глобал', 'OFS', 'Главная организация', 1, 'holding'))
    print("Добавлена организация в таблицу")

    # Фиксируем изменения
    conn.commit()
    print("Изменения зафиксированы")

    # Проверяем, что организация создана
    cursor.execute('SELECT * FROM organizations')
    row = cursor.fetchone()
    print(f"Организация успешно создана!")
    print(f"ID: {row[0]}")
    print(f"Название: {row[1]}")
    print(f"Код: {row[2]}")
    print(f"Описание: {row[3]}")
    print(f"Тип: {row[5]}")

    # Закрываем соединение
    conn.close()
    print("Соединение с базой данных закрыто")
    
except Exception as e:
    print(f"Произошла ошибка: {e}")
    print(traceback.format_exc())
    
print("Скрипт завершен") 