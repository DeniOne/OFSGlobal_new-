#!/usr/bin/env python
"""
Скрипт для просмотра данных из базы данных.
"""

import sqlite3

# Подключаемся к БД
conn = sqlite3.connect("full_api_new.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def print_table_data(table_name, limit=10):
    """Печатает данные из таблицы"""
    print(f"\n=== {table_name.upper()} ===")
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    rows = cursor.fetchall()
    
    if not rows:
        print("Таблица пуста")
        return
    
    # Получаем имена столбцов
    columns = [description[0] for description in cursor.description]
    print(", ".join(columns))
    print("-" * 80)
    
    # Печатаем данные
    for row in rows:
        values = [str(row[col]) for col in columns]
        print(" | ".join(values))

# Организации
print("\n*** ОРГАНИЗАЦИИ ***")
cursor.execute("""
SELECT id, name, code, org_type, parent_id, is_active 
FROM organizations 
ORDER BY id
""")
for row in cursor.fetchall():
    parent = f"(Родитель: {row['parent_id']})" if row['parent_id'] else ""
    active = "Активна" if row['is_active'] else "Неактивна"
    print(f"- ID {row['id']}: {row['name']} ({row['code']}) - {row['org_type']} {parent} - {active}")

# Подразделения
print("\n*** ПОДРАЗДЕЛЕНИЯ ***")
cursor.execute("""
SELECT d.id, d.name, d.code, d.organization_id, o.name as org_name, d.parent_id, p.name as parent_name, d.is_active
FROM divisions d 
LEFT JOIN organizations o ON d.organization_id = o.id
LEFT JOIN divisions p ON d.parent_id = p.id
ORDER BY d.id
""")
for row in cursor.fetchall():
    parent = f"(Родитель: {row['parent_id']} - {row['parent_name']})" if row['parent_id'] else ""
    active = "Активно" if row['is_active'] else "Неактивно"
    print(f"- ID {row['id']}: {row['name']} ({row['code']}) - Орг: {row['org_name']} {parent} - {active}")

# Функции
print("\n*** ФУНКЦИИ ***")
cursor.execute("SELECT id, name, code, description, is_active FROM functions ORDER BY id")
for row in cursor.fetchall():
    active = "Активна" if row['is_active'] else "Неактивна"
    print(f"- ID {row['id']}: {row['name']} ({row['code']}) - {row['description']} - {active}")

# Секции
print("\n*** СЕКЦИИ ***")
cursor.execute("SELECT id, name, code, description, is_active FROM sections ORDER BY id")
for row in cursor.fetchall():
    active = "Активна" if row['is_active'] else "Неактивна"
    print(f"- ID {row['id']}: {row['name']} ({row['code']}) - {row['description']} - {active}")

# Должности
print("\n*** ДОЛЖНОСТИ ***")
cursor.execute("""
SELECT p.id, p.name, p.code, p.function_id, f.name as function_name, p.is_active
FROM positions p
LEFT JOIN functions f ON p.function_id = f.id
ORDER BY p.id
""")
for row in cursor.fetchall():
    function = f"Функция: {row['function_name']}" if row['function_id'] else "Без функции"
    active = "Активна" if row['is_active'] else "Неактивна"
    print(f"- ID {row['id']}: {row['name']} ({row['code']}) - {function} - {active}")

# Сотрудники
print("\n*** СОТРУДНИКИ ***")
cursor.execute("""
SELECT s.id, s.first_name, s.last_name, s.email, s.organization_id, o.name as org_name, 
       s.primary_organization_id, po.name as primary_org_name
FROM staff s
LEFT JOIN organizations o ON s.organization_id = o.id
LEFT JOIN organizations po ON s.primary_organization_id = po.id
ORDER BY s.id
LIMIT 10
""")
for row in cursor.fetchall():
    org = f"Орг: {row['org_name']}" if row['organization_id'] else "Без организации"
    primary_org = f"Основная орг: {row['primary_org_name']}" if row['primary_organization_id'] else "Без основной организации"
    print(f"- ID {row['id']}: {row['first_name']} {row['last_name']} ({row['email']}) - {org}, {primary_org}")

# Должности сотрудников
print("\n*** ДОЛЖНОСТИ СОТРУДНИКОВ ***")
cursor.execute("""
SELECT sp.id, sp.staff_id, s.first_name || ' ' || s.last_name as staff_name, 
       sp.position_id, p.name as position_name, sp.division_id, d.name as division_name,
       sp.is_primary, sp.start_date, sp.end_date
FROM staff_positions sp
JOIN staff s ON sp.staff_id = s.id
JOIN positions p ON sp.position_id = p.id
LEFT JOIN divisions d ON sp.division_id = d.id
ORDER BY sp.staff_id, sp.is_primary DESC
LIMIT 15
""")
for row in cursor.fetchall():
    primary = "Основная" if row['is_primary'] else "Дополнительная"
    division = f"в {row['division_name']}" if row['division_id'] else "без подразделения"
    end_date = f" до {row['end_date']}" if row['end_date'] else ""
    print(f"- ID {row['id']}: {row['staff_name']} - {row['position_name']} {division} ({primary}, с {row['start_date']}{end_date})")

# Локации сотрудников
print("\n*** ЛОКАЦИИ СОТРУДНИКОВ ***")
cursor.execute("""
SELECT sl.id, sl.staff_id, s.first_name || ' ' || s.last_name as staff_name, 
       sl.location_id, o.name as location_name, sl.is_current, sl.date_from, sl.date_to
FROM staff_locations sl
JOIN staff s ON sl.staff_id = s.id
JOIN organizations o ON sl.location_id = o.id
ORDER BY sl.staff_id, sl.is_current DESC
LIMIT 10
""")
for row in cursor.fetchall():
    current = "Текущая" if row['is_current'] else "Предыдущая"
    end_date = f" до {row['date_to']}" if row['date_to'] else ""
    print(f"- ID {row['id']}: {row['staff_name']} - {row['location_name']} ({current}, с {row['date_from']}{end_date})")

# Функциональные отношения
print("\n*** ФУНКЦИОНАЛЬНЫЕ ОТНОШЕНИЯ ***")
cursor.execute("""
SELECT fr.id, fr.manager_id, m.first_name || ' ' || m.last_name as manager_name,
       fr.subordinate_id, s.first_name || ' ' || s.last_name as subordinate_name,
       fr.relation_type, fr.is_active, fr.start_date, fr.end_date
FROM functional_relations fr
JOIN staff m ON fr.manager_id = m.id
JOIN staff s ON fr.subordinate_id = s.id
ORDER BY fr.relation_type, fr.manager_id
LIMIT 15
""")
for row in cursor.fetchall():
    active = "Активно" if row['is_active'] else "Неактивно"
    end_date = f" до {row['end_date']}" if row['end_date'] else ""
    print(f"- ID {row['id']}: {row['manager_name']} -> {row['subordinate_name']} ({row['relation_type']}, {active}, с {row['start_date']}{end_date})")

conn.close() 