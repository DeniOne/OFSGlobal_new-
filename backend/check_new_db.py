#!/usr/bin/env python
"""
Скрипт для проверки новой базы данных и ее структуры.
"""

import sqlite3
import json

# Подключаемся к БД
conn = sqlite3.connect("full_api_new.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Получаем список всех таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [table[0] for table in cursor.fetchall()]

print("Таблицы в новой базе данных:")
for table in tables:
    print(f"- {table}")

# Проверяем таблицы и количество записей
print("\nСтатистика по таблицам:")
for table in tables:
    if table == "sqlite_sequence":
        continue
    
    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
    count = cursor.fetchone()["count"]
    print(f"- {table}: {count} записей")

# Проверяем структуру таблицы staff
print("\nПроверка таблицы staff:")
cursor.execute("PRAGMA table_info(staff)")
columns = cursor.fetchall()
print("Структура таблицы:")
for col in columns:
    print(f"  - {col['name']} ({col['type']}), NOT NULL: {col['notnull'] == 1}")

# Проверяем сотрудников с несколькими должностями
print("\nСотрудники с несколькими должностями:")
cursor.execute("""
SELECT s.id, s.first_name, s.last_name, COUNT(sp.id) as position_count
FROM staff s
JOIN staff_positions sp ON s.id = sp.staff_id
GROUP BY s.id
HAVING position_count > 1
""")
multi_position_staff = cursor.fetchall()
for staff in multi_position_staff:
    print(f"  - ID {staff['id']}: {staff['first_name']} {staff['last_name']} ({staff['position_count']} должностей)")

    # Вывести должности для этого сотрудника
    cursor.execute("""
    SELECT p.name as position_name, d.name as division_name, sp.is_primary, sp.start_date
    FROM staff_positions sp
    JOIN positions p ON sp.position_id = p.id
    LEFT JOIN divisions d ON sp.division_id = d.id
    WHERE sp.staff_id = ?
    """, (staff['id'],))
    positions = cursor.fetchall()
    for pos in positions:
        primary_str = "основная" if pos['is_primary'] else "дополнительная"
        print(f"    • {pos['position_name']} в {pos['division_name']} ({primary_str}, с {pos['start_date']})")

# Проверяем функциональные отношения
print("\nФункциональные отношения:")
cursor.execute("""
SELECT fr.relation_type, COUNT(*) as count
FROM functional_relations fr
GROUP BY fr.relation_type
""")
relation_stats = cursor.fetchall()
for rel in relation_stats:
    print(f"  - {rel['relation_type']}: {rel['count']} отношений")

conn.close() 