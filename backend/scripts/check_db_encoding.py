#!/usr/bin/env python
"""
Скрипт для проверки настроек кодировки в базе данных PostgreSQL.
Проверяет текущую кодировку БД и настраивает правильную UTF-8 при необходимости.
"""
import asyncio
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
sys.path.append(".")

from app.core.config import settings

def print_header(text):
    """Выводит заголовок с подчеркиванием"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

async def check_encoding():
    """Проверяет текущие настройки кодировки в базе данных"""
    print_header("Проверка настроек кодировки в PostgreSQL")
    
    # Подключаемся к PostgreSQL
    try:
        conn = psycopg2.connect(
            host=settings.POSTGRES_SERVER,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Проверяем кодировку базы данных
        cursor.execute("SHOW server_encoding;")
        server_encoding = cursor.fetchone()[0]
        print(f"Кодировка сервера: {server_encoding}")
        
        cursor.execute("SHOW client_encoding;")
        client_encoding = cursor.fetchone()[0]
        print(f"Кодировка клиента: {client_encoding}")
        
        # Проверяем текущую базу данных
        cursor.execute(f"SELECT datname, pg_encoding_to_char(encoding) FROM pg_database WHERE datname = '{settings.POSTGRES_DB}';")
        db_info = cursor.fetchone()
        if db_info:
            print(f"База данных '{db_info[0]}' использует кодировку: {db_info[1]}")
        
        # Устанавливаем кодировку клиента, если она не UTF8
        if client_encoding.lower() != 'utf8':
            print("Устанавливаем кодировку клиента UTF8...")
            cursor.execute("SET client_encoding TO 'UTF8';")
            cursor.execute("SHOW client_encoding;")
            new_client_encoding = cursor.fetchone()[0]
            print(f"Новая кодировка клиента: {new_client_encoding}")
        
        print("\nРекомендации:")
        if server_encoding.lower() != 'utf8':
            print("ВНИМАНИЕ: Кодировка сервера не UTF8. Рекомендуется пересоздать кластер PostgreSQL с кодировкой UTF8.")
            
        print("\nПроверка успешно завершена!")
        
    except Exception as e:
        print(f"Ошибка при подключении к PostgreSQL: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    asyncio.run(check_encoding()) 