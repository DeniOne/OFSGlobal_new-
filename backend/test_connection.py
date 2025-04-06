import os
from dotenv import load_dotenv
import psycopg2

# Загружаем переменные окружения
load_dotenv()

# Получаем параметры подключения
params = {
    'host': os.getenv("POSTGRES_SERVER", "localhost"),
    'user': os.getenv("POSTGRES_USER", "postgres"),
    'password': os.getenv("POSTGRES_PASSWORD", "password"),
    'database': os.getenv("POSTGRES_DB", "ofs_db"),
    'port': os.getenv("POSTGRES_PORT", "5432")
}

# Выводим параметры подключения
print("Параметры подключения:")
for key, value in params.items():
    print(f"{key}: {value}")

# Пробуем подключиться
try:
    conn = psycopg2.connect(**params)
    print("\nПодключение успешно!")
    conn.close()
except Exception as e:
    print(f"\nОшибка подключения: {e}") 