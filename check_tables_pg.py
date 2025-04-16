#!/usr/bin/env python
"""
Скрипт для проверки структуры и данных таблиц в PostgreSQL.
Выводит список таблиц, их структуру, количество записей и информацию о связях.
"""

import asyncio
import asyncpg
import sys
from datetime import datetime

# Параметры подключения к PostgreSQL
PG_USER = "postgres"
PG_PASSWORD = "111"  # Правильный пароль
PG_SERVER = "localhost"
PG_DATABASE = "postgres"  # Сначала подключимся к стандартной базе
PG_PORT = 5432

async def list_databases():
    """Получает список всех доступных баз данных"""
    conn = None
    try:
        # Подключение к базе данных PostgreSQL
        conn = await asyncpg.connect(
            user=PG_USER, 
            password=PG_PASSWORD,
            database=PG_DATABASE, 
            host=PG_SERVER,
            port=PG_PORT,
            timeout=30.0
        )
        
        # Получаем список баз данных
        databases = await conn.fetch("""
            SELECT datname FROM pg_database 
            WHERE datistemplate = false
            ORDER BY datname;
        """)
        
        print("Доступные базы данных:")
        db_names = []
        for db in databases:
            db_name = db['datname']
            print(f"- {db_name}")
            db_names.append(db_name)
        
        return db_names
    except Exception as e:
        print(f"Ошибка при получении списка баз данных: {str(e)}")
        return []
    finally:
        if conn:
            await conn.close()

async def check_database(database_name):
    """Проверяет структуру указанной базы данных"""
    with open(f'pg_check_{database_name}.txt', 'w', encoding='utf-8') as output_file:
        conn = None
        try:
            # Подключение к базе данных PostgreSQL
            conn = await asyncpg.connect(
                user=PG_USER, 
                password=PG_PASSWORD,
                database=database_name, 
                host=PG_SERVER,
                port=PG_PORT,
                timeout=30.0
            )
            
            output_msg = f"Успешное подключение к базе данных {database_name} на сервере {PG_SERVER}\n\n"
            print(output_msg)
            output_file.write(output_msg)
            
            # Получение списка таблиц
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            result = f"В базе данных найдено {len(tables)} таблиц:\n"
            print(result)
            output_file.write(result)
            
            # Проверка каждой таблицы
            for table in tables:
                table_name = table['table_name']
                
                # Информация о структуре таблицы
                columns = await conn.fetch("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = $1
                    ORDER BY ordinal_position
                """, table_name)
                
                # Количество записей в таблице
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                
                # Получение первичных ключей
                primary_keys = await conn.fetch("""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu 
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.constraint_type = 'PRIMARY KEY' 
                        AND tc.table_schema = 'public' 
                        AND tc.table_name = $1
                """, table_name)
                
                # Получение внешних ключей
                foreign_keys = await conn.fetch("""
                    SELECT
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY' 
                        AND tc.table_schema = 'public'
                        AND tc.table_name = $1
                """, table_name)
                
                # Вывод информации о таблице
                table_info = f"===== Таблица: {table_name} =====\n"
                table_info += "Столбцы:\n"
                for column in columns:
                    nullable = "NULLABLE" if column['is_nullable'] == 'YES' else "NOT NULL"
                    table_info += f"  - {column['column_name']} ({column['data_type']}) {nullable}\n"
                
                table_info += f"Количество записей: {count}\n"
                
                if primary_keys:
                    pk_names = ", ".join([pk['column_name'] for pk in primary_keys])
                    table_info += f"Первичные ключи: {pk_names}\n"
                
                if foreign_keys:
                    table_info += "Внешние ключи:\n"
                    for fk in foreign_keys:
                        table_info += f"  - {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}\n"
                
                # Примеры данных (если есть записи)
                if count > 0:
                    examples = await conn.fetch(f"SELECT * FROM {table_name} LIMIT 2")
                    table_info += "Примеры данных:\n"
                    for example in examples:
                        table_info += f"  {dict(example)}\n"
                
                print(table_info)
                output_file.write(table_info + "\n")
            
            # Проверка последовательностей
            sequences = await conn.fetch("""
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_schema = 'public'
            """)
            
            seq_info = f"\nПоследовательности ({len(sequences)}):\n"
            for seq in sequences:
                seq_name = seq['sequence_name']
                # Получение текущего значения последовательности
                curr_val = await conn.fetchval(f"SELECT last_value FROM {seq_name}")
                seq_info += f"  - {seq_name}: текущее значение = {curr_val}\n"
            
            print(seq_info)
            output_file.write(seq_info + "\n")
            
            # Проверка версии Alembic
            try:
                alembic_version = await conn.fetchval("SELECT version_num FROM alembic_version")
                ver_info = f"\nТекущая версия Alembic: {alembic_version}\n"
                print(ver_info)
                output_file.write(ver_info + "\n")
            except Exception as e:
                ver_error = f"\nНе удалось получить версию Alembic: {str(e)}\n"
                print(ver_error)
                output_file.write(ver_error + "\n")
            
        except Exception as e:
            error_msg = f"Ошибка при проверке базы данных: {str(e)}"
            print(error_msg)
            output_file.write(error_msg + "\n")
        finally:
            # Закрытие соединения
            if conn:
                await conn.close()
                closing_msg = "Соединение с базой данных закрыто."
                print(closing_msg)
                output_file.write(closing_msg + "\n")

async def main():
    """Основная функция скрипта"""
    # Сначала получаем список всех баз данных
    databases = await list_databases()
    
    # Проверяем интересующие нас базы
    target_dbs = ["ofs_global", "ofs_db_new", "ofs_db", "ofs"]
    
    # Добавляем все имеющиеся базы (на случай, если имя базы нестандартное)
    for db in databases:
        if db not in target_dbs and db != "postgres" and db != "template0" and db != "template1":
            target_dbs.append(db)
    
    # Проверяем каждую из баз
    for db in target_dbs:
        print(f"\nПроверка базы данных: {db}")
        try:
            await check_database(db)
            print(f"Результаты проверки {db} сохранены в файл pg_check_{db}.txt")
        except Exception as e:
            print(f"Ошибка при проверке {db}: {str(e)}")

# Запуск асинхронной функции
asyncio.run(main())
print("Проверка завершена.") 