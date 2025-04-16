#!/usr/bin/env python
"""
Простой скрипт для проверки подключения к PostgreSQL с использованием psycopg2
"""

import psycopg2
import sys

def test_connection():
    try:
        # Попытка подключения к PostgreSQL с основными параметрами
        conn = psycopg2.connect(
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432",
            database="postgres", # Пробуем подключиться к стандартной БД postgres
            client_encoding='utf8'
        )
        
        # Если соединение успешно, выводим информацию
        print("Успешное подключение к PostgreSQL:")
        cursor = conn.cursor()
        
        # Получаем версию PostgreSQL
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"Версия PostgreSQL: {db_version[0]}")
        
        # Получаем список баз данных
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = cursor.fetchall()
        print("\nДоступные базы данных:")
        for db in databases:
            print(f"- {db[0]}")
            
        cursor.close()
        conn.close()
        print("\nСоединение с PostgreSQL закрыто.")
        
    except (Exception, psycopg2.Error) as error:
        print(f"Ошибка при подключении к PostgreSQL: {str(error)}")
        
        # Пробуем с другим паролем
        print("\nПопытка подключения с другим паролем...")
        for test_password in ["", "111", "admin", "postgresql"]:
            print(f"Тестирую пароль: {test_password if test_password else '[пустой]'}")
            try:
                conn = psycopg2.connect(
                    user="postgres",
                    password=test_password,
                    host="localhost",
                    port="5432",
                    database="postgres",
                    client_encoding='utf8'
                )
                print(f"Подключение успешно с паролем: {test_password if test_password else '[пустой]'}!")
                conn.close()
                break
            except (Exception, psycopg2.Error) as inner_error:
                print(f"  Неудача: {str(inner_error)}")

# Выполняем тест подключения
if __name__ == "__main__":
    test_connection() 