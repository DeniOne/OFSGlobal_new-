# backend/seed_db.py
import sqlite3
import os
from datetime import datetime

DB_PATH = "full_api_new.db"

# --- Тестовые данные ---

# Сначала создадим пару организаций, чтобы были ID
# Убедись, что типы org_type соответствуют enum в full_api.py
organizations_data = [
    ('ООО "Рога и Копыта"', 'RK-001', 'Основной холдинг', 'holding', 1, None, 'RK-MAIN', '1111111111', '111001001', 'Адрес холдинга', 'Адрес холдинга'),
    ('ИП Рогов Р.Р.', 'IP-ROG', 'Дочерняя компания', 'legal_entity', 1, 1, 'IP-ROG-CP', '2222222222', '222001001', 'Юр. адрес Рогова', 'Факт. адрес Рогова'),
    ('Филиал "Западный"', 'RK-ZAP', 'Локация на западе', 'location', 1, 1, 'RK-ZAP-CP', None, None, 'Адрес локации Запад', 'Адрес локации Запад'),
    ('Филиал "Восточный"', 'RK-VOS', 'Локация на востоке', 'location', 1, 1, 'RK-VOS-CP', None, None, 'Адрес локации Восток', 'Адрес локации Восток'),
]

staff_data = [
    {
        "email": "ivanov@example.com", "first_name": "Иван", "last_name": "Иванов", "middle_name": "Иванович",
        "phone": "+7 999 111 11 11", "position": "Директор", "description": "Главный директор",
        "is_active": 1, "organization_id": 2, "primary_organization_id": 1, "location_id": 3, # Привязан к ИП Рогов (орг), Рога и Копыта (холд), Западный (локация)
        "registration_address": "111111, Москва, ул. Ленина, д. 1, кв. 10",
        "actual_address": "111111, Москва, ул. Ленина, д. 1, кв. 10",
        "telegram_id": "@ivan_ivanov", "vk": "vk.com/ivan", "instagram": "insta_ivan"
    },
    {
        "email": "petrov@example.com", "first_name": "Петр", "last_name": "Петров", "middle_name": None,
        "phone": "+7 999 222 22 22", "position": "Менеджер", "description": "Старший менеджер",
        "is_active": 1, "organization_id": 2, "primary_organization_id": 1, "location_id": 4, # Привязан к ИП Рогов (орг), Рога и Копыта (холд), Восточный (локация)
        "registration_address": "222222, Питер, ул. Садовая, д. 5",
        "actual_address": "222222, Питер, ул. Садовая, д. 5",
        "telegram_id": "@petr_petrov", "vk": None, "instagram": None
    },
    {
        "email": "sidorova@example.com", "first_name": "Анна", "last_name": "Сидорова", "middle_name": "Петровна",
        "phone": "+7 999 333 33 33", "position": "Бухгалтер", "description": None,
        "is_active": 0, "organization_id": 2, "primary_organization_id": 1, "location_id": 3, # Неактивный сотрудник
        "registration_address": "333333, Казань, ул. Баумана, д. 15",
        "actual_address": "333333, Казань, ул. Баумана, д. 15",
        "telegram_id": "@anna_sid", "vk": "vk.com/anna", "instagram": None
    },
]

# --- Функции для заполнения ---

def create_connection(db_file):
    """Создает соединение с базой данных SQLite."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Соединение с {db_file} установлено.")
    except sqlite3.Error as e:
        print(f"Ошибка соединения с БД: {e}")
    return conn

def insert_organization(conn, org_data):
    """Вставляет одну организацию."""
    sql = ''' INSERT INTO organizations(name, code, description, org_type, is_active, parent_id, ckp, inn, kpp, legal_address, physical_address, created_at, updated_at)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    try:
        now = datetime.now().isoformat()
        cur.execute(sql, org_data + (now, now))
        # print(f"Организация '{org_data[0]}' добавлена, ID: {cur.lastrowid}")
        return cur.lastrowid
    except sqlite3.IntegrityError as e:
        print(f"Ошибка добавления организации '{org_data[0]}': {e} (возможно, уже существует)")
        # Попробуем найти существующую
        cur.execute("SELECT id FROM organizations WHERE code = ?", (org_data[1],))
        row = cur.fetchone()
        return row[0] if row else None
    except sqlite3.Error as e:
        print(f"Ошибка SQLite при добавлении организации '{org_data[0]}': {e}")
        return None


def insert_staff(conn, staff_member):
    """Вставляет одного сотрудника."""
    # Убедимся, что все ключи есть, даже если None
    columns = [
        'email', 'first_name', 'last_name', 'middle_name', 'phone',
        'position', 'description', 'is_active', 'organization_id',
        'primary_organization_id', 'location_id', 'registration_address',
        'actual_address', 'telegram_id', 'vk', 'instagram'
    ]
    values = [staff_member.get(col) for col in columns]

    sql = f''' INSERT INTO staff({", ".join(columns)}, created_at, updated_at)
              VALUES({", ".join(["?"] * len(columns))}, ?, ?) '''
    cur = conn.cursor()
    try:
        now = datetime.now().isoformat()
        cur.execute(sql, values + [now, now])
        print(f"Сотрудник '{staff_member.get('email')}' добавлен, ID: {cur.lastrowid}")
        return cur.lastrowid
    except sqlite3.IntegrityError as e:
         print(f"Ошибка добавления сотрудника '{staff_member.get('email')}': {e} (возможно, уже существует)")
         return None
    except sqlite3.Error as e:
        print(f"Ошибка SQLite при добавлении сотрудника '{staff_member.get('email')}': {e}")
        return None

# --- Основная логика скрипта ---

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print(f"Ошибка: Файл базы данных '{DB_PATH}' не найден.")
        print("Сначала запустите бэкенд (run_servers.bat) один раз, чтобы он создал пустую базу данных.")
    else:
        conn = create_connection(DB_PATH)
        if conn is not None:
            print("\n--- Добавление организаций ---")
            org_ids = {}
            for org_data in organizations_data:
                org_id = insert_organization(conn, org_data)
                if org_id:
                    org_ids[org_data[1]] = org_id # Сохраняем ID по коду

            # Обновим тестовые данные сотрудников реальными ID организаций (если они были созданы/найдены)
            # Это простой пример, можно сделать сложнее с привязкой по кодам
            if org_ids.get('IP-ROG'):
                staff_data[0]['organization_id'] = org_ids['IP-ROG']
                staff_data[1]['organization_id'] = org_ids['IP-ROG']
                staff_data[2]['organization_id'] = org_ids['IP-ROG']
            if org_ids.get('RK-001'):
                 staff_data[0]['primary_organization_id'] = org_ids['RK-001']
                 staff_data[1]['primary_organization_id'] = org_ids['RK-001']
                 staff_data[2]['primary_organization_id'] = org_ids['RK-001']
            if org_ids.get('RK-ZAP'):
                 staff_data[0]['location_id'] = org_ids['RK-ZAP']
                 staff_data[2]['location_id'] = org_ids['RK-ZAP']
            if org_ids.get('RK-VOS'):
                 staff_data[1]['location_id'] = org_ids['RK-VOS']


            print("\n--- Добавление сотрудников ---")
            for staff_member in staff_data:
                insert_staff(conn, staff_member)

            conn.commit()
            conn.close()
            print("\nЗаполнение тестовыми данными завершено.")
        else:
            print("Не удалось установить соединение с БД.")
