import sqlite3
import json

# Подключаемся к БД
conn = sqlite3.connect('full_api_new.db')
cursor = conn.cursor()

# Получаем все ЦКП
cursor.execute('SELECT * FROM valuable_final_products')
rows = cursor.fetchall()

# Выводим результаты
for row in rows:
    print("\nЦКП #{}:".format(row[0]))
    print("Тип сущности:", row[1])
    print("ID сущности:", row[2])
    print("Название:", row[3])
    print("Описание:", row[4])
    print("Метрики:", json.loads(row[5]) if row[5] else None)
    print("Статус:", row[6])
    print("Прогресс:", row[7])
    print("Дата начала:", row[8])
    print("Целевая дата:", row[9])
    print("Активен:", bool(row[10]))
    print("Создан:", row[11])
    print("Обновлен:", row[12])
    print("-" * 50) 