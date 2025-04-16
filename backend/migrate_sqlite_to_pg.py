#!/usr/bin/env python
"""
Скрипт для миграции данных из SQLite в PostgreSQL.

Этот скрипт переносит все таблицы и данные из SQLite в PostgreSQL,
учитывая особенности обеих СУБД. Проверяет структуру таблиц и 
обнаруживает отсутствующие таблицы и столбцы.

Для работы скрипта требуются:
- Установленный pandas
- Доступ к SQLite БД
- Настроенный PostgreSQL

Запуск:
python migrate_sqlite_to_pg.py
"""

import sqlite3
import pandas as pd
import logging
from sqlalchemy import create_engine, text, inspect
import psycopg2
import os
import sys
from datetime import datetime
import argparse
import time
import numpy as np

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pg_migration.log")
    ]
)
logger = logging.getLogger("sqlite_to_pg_migration")

# Параметры подключения
SQLITE_DB_PATH = "backend/full_api_new.db"
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "111")
PG_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
PG_DB = os.getenv("POSTGRES_DB", "ofs_db_new")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

# Строка подключения к PostgreSQL
PG_CONNECTION_STRING = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_SERVER}:{PG_PORT}/{PG_DB}"

# Маппинг типов между SQLite и PostgreSQL
TYPE_MAP = {
    'INTEGER': 'INTEGER',
    'TEXT': 'TEXT',
    'REAL': 'FLOAT',
    'BLOB': 'BYTEA',
    'DATE': 'DATE',
    'TIMESTAMP': 'TIMESTAMP',
    'VARCHAR(20)': 'VARCHAR(20)',
    'BOOLEAN': 'BOOLEAN'
}

# Список зарезервированных слов PostgreSQL, которые нужно заключать в кавычки
RESERVED_WORDS = [
    'user', 'table', 'group', 'order', 'select', 'from', 'where', 'join',
    'limit', 'offset', 'with', 'create', 'update', 'delete', 'index',
    'constraint', 'function', 'position', 'left', 'right', 'inner'
]

def quote_identifier(identifier):
    """Заключает идентификатор в двойные кавычки, если он является зарезервированным словом"""
    if identifier.lower() in RESERVED_WORDS:
        return f'"{identifier}"'
    return identifier

def backup_sqlite_db():
    """Создает резервную копию SQLite базы данных перед миграцией"""
    backup_name = f"full_api_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    if os.path.exists(SQLITE_DB_PATH):
        import shutil
        shutil.copy2(SQLITE_DB_PATH, backup_name)
        logger.info(f"Создана резервная копия SQLite базы данных: {backup_name}")
    else:
        logger.error(f"База данных {SQLITE_DB_PATH} не найдена!")
        sys.exit(1)
    
    return backup_name

def create_db_connections():
    """Создает соединения с базами данных"""
    try:
        # Подключение к SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        logger.info(f"Успешное подключение к SQLite базе данных: {SQLITE_DB_PATH}")
        
        # Подключение к PostgreSQL
        pg_engine = create_engine(PG_CONNECTION_STRING, isolation_level='AUTOCOMMIT')
        logger.info(f"Успешное подключение к PostgreSQL базе данных: {PG_DB}")
        
        # Проверяем подключение к PostgreSQL
        with pg_engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"Версия PostgreSQL: {version}")
        
        return sqlite_conn, pg_engine
    except Exception as e:
        logger.error(f"Ошибка при подключении к базам данных: {str(e)}")
        sys.exit(1)

def get_sqlite_tables(sqlite_conn):
    """Получает список таблиц из SQLite базы данных"""
    try:
        tables_df = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';",
            sqlite_conn
        )
        tables = tables_df['name'].tolist()
        logger.info(f"Найдено {len(tables)} таблиц в SQLite базе данных: {', '.join(tables)}")
        return tables
    except Exception as e:
        logger.error(f"Ошибка при получении списка таблиц: {str(e)}")
        sys.exit(1)

def get_pg_tables(pg_engine):
    """Получает список существующих таблиц в PostgreSQL"""
    try:
        inspector = inspect(pg_engine)
        tables = inspector.get_table_names()
        tables = [t for t in tables if t != 'alembic_version']
        logger.info(f"Найдено {len(tables)} таблиц в PostgreSQL: {', '.join(tables)}")
        return tables
    except Exception as e:
        logger.error(f"Ошибка при получении списка таблиц PostgreSQL: {str(e)}")
        return []

def get_sqlite_table_structure(sqlite_conn, table_name):
    """Получает структуру таблицы SQLite"""
    try:
        cursor = sqlite_conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        structure = {col[1]: col[2] for col in columns}
        logger.debug(f"Структура таблицы SQLite {table_name}: {structure}")
        return structure
    except Exception as e:
        logger.error(f"Ошибка при получении структуры таблицы {table_name}: {str(e)}")
        return {}

def get_pg_table_structure(pg_engine, table_name):
    """Получает структуру таблицы PostgreSQL"""
    try:
        quoted_table_name = quote_identifier(table_name)
        inspector = inspect(pg_engine)
        columns = inspector.get_columns(table_name)
        structure = {col['name']: str(col['type']) for col in columns}
        logger.debug(f"Структура таблицы PostgreSQL {table_name}: {structure}")
        return structure
    except Exception as e:
        logger.error(f"Ошибка при получении структуры таблицы PostgreSQL {table_name}: {str(e)}")
        return {}

def create_pg_table(pg_engine, table_name, structure):
    """Создает таблицу в PostgreSQL на основе структуры SQLite"""
    try:
        quoted_table_name = quote_identifier(table_name)
        column_defs = []
        for col_name, col_type in structure.items():
            pg_type = TYPE_MAP.get(col_type, 'TEXT')
            quoted_col_name = quote_identifier(col_name)
            if col_name.lower() == 'id':
                column_defs.append(f"{quoted_col_name} SERIAL PRIMARY KEY")
            else:
                column_defs.append(f"{quoted_col_name} {pg_type}")
                
        create_table_sql = f"CREATE TABLE {quoted_table_name} (\n    " + ",\n    ".join(column_defs) + "\n);"
        logger.info(f"SQL для создания таблицы: {create_table_sql}")
        
        with pg_engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
            
        logger.info(f"Создана таблица {table_name} в PostgreSQL")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании таблицы {table_name}: {str(e)}")
        logger.error(f"SQL запрос: {create_table_sql if 'create_table_sql' in locals() else 'не создан'}")
        return False

def add_missing_columns(pg_engine, table_name, sqlite_structure, pg_structure):
    """Добавляет отсутствующие столбцы в таблицу PostgreSQL"""
    try:
        quoted_table_name = quote_identifier(table_name)
        missing_columns = {}
        for col_name, col_type in sqlite_structure.items():
            if col_name.lower() not in [c.lower() for c in pg_structure.keys()]:
                missing_columns[col_name] = col_type
        
        if not missing_columns:
            logger.info(f"Нет отсутствующих столбцов в таблице {table_name}")
            return True
        
        logger.info(f"Добавление {len(missing_columns)} отсутствующих столбцов в таблицу {table_name}: {', '.join(missing_columns.keys())}")
        
        for col_name, col_type in missing_columns.items():
            quoted_col_name = quote_identifier(col_name)
            pg_type = TYPE_MAP.get(col_type, 'TEXT')
            alter_sql = f"ALTER TABLE {quoted_table_name} ADD COLUMN {quoted_col_name} {pg_type};"
            logger.info(f"SQL для добавления столбца: {alter_sql}")
            
            with pg_engine.connect() as conn:
                conn.execute(text(alter_sql))
                conn.commit()
            
            logger.info(f"Добавлен столбец {col_name} ({pg_type}) в таблицу {table_name}")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при добавлении столбцов в таблицу {table_name}: {str(e)}")
        return False

def convert_data_types(df, pg_structure):
    """Преобразует типы данных из SQLite в типы PostgreSQL"""
    logger.info("Преобразование типов данных...")
    
    # Создаем копию DataFrame, чтобы не изменять исходный
    df_converted = df.copy()
    
    # Проходим по всем столбцам в структуре PostgreSQL
    for col_name, pg_type in pg_structure.items():
        if col_name in df_converted.columns:
            # Преобразование INTEGER в BOOLEAN
            if 'boolean' in pg_type.lower() and df_converted[col_name].dtype in (np.int64, np.int32, np.int16, np.int8):
                logger.info(f"Преобразование столбца {col_name} из INTEGER в BOOLEAN")
                df_converted[col_name] = df_converted[col_name].astype(bool)
            
            # Преобразование дат и времени
            elif 'timestamp' in pg_type.lower() or 'date' in pg_type.lower():
                try:
                    if df_converted[col_name].dtype == 'object':
                        logger.info(f"Преобразование столбца {col_name} в datetime")
                        df_converted[col_name] = pd.to_datetime(df_converted[col_name], errors='coerce')
                except Exception as e:
                    logger.warning(f"Ошибка при преобразовании столбца {col_name} в datetime: {str(e)}")
            
            # Преобразование числовых типов
            elif 'integer' in pg_type.lower() and df_converted[col_name].dtype not in (np.int64, np.int32, np.int16, np.int8):
                try:
                    logger.info(f"Преобразование столбца {col_name} в INTEGER")
                    df_converted[col_name] = df_converted[col_name].astype(int)
                except Exception as e:
                    logger.warning(f"Ошибка при преобразовании столбца {col_name} в INTEGER: {str(e)}")
            
            # Преобразование строковых типов для VARCHAR с ограничением длины
            elif 'varchar' in pg_type.lower() and df_converted[col_name].dtype == 'object':
                # Извлекаем ограничение длины, если оно есть
                import re
                length_match = re.search(r'varchar\((\d+)\)', pg_type.lower())
                if length_match:
                    max_length = int(length_match.group(1))
                    logger.info(f"Проверка длины строк в столбце {col_name} (максимум {max_length} символов)")
                    # Обрезаем строки, превышающие максимальную длину
                    long_strings = df_converted[col_name].astype(str).apply(len) > max_length
                    if long_strings.any():
                        logger.warning(f"Обнаружены строки, превышающие максимальную длину в столбце {col_name}")
                        df_converted.loc[long_strings, col_name] = df_converted.loc[long_strings, col_name].astype(str).str[:max_length]
    
    logger.info("Преобразование типов данных завершено")
    return df_converted

def migrate_table(sqlite_conn, pg_engine, table_name, force=False):
    """Мигрирует данные из таблицы SQLite в PostgreSQL"""
    start_time = time.time()
    logger.info(f"Начало миграции таблицы {table_name}...")
    
    try:
        quoted_table_name = quote_identifier(table_name)
        
        # Проверяем, существует ли таблица в PostgreSQL
        pg_tables = get_pg_tables(pg_engine)
        table_exists = table_name.lower() in [t.lower() for t in pg_tables]
        
        # Получаем структуру таблицы SQLite
        sqlite_structure = get_sqlite_table_structure(sqlite_conn, table_name)
        if not sqlite_structure:
            logger.error(f"Не удалось получить структуру таблицы {table_name} в SQLite")
            return 0
        
        # Если таблица не существует, создаем ее
        if not table_exists:
            logger.info(f"Таблица {table_name} отсутствует в PostgreSQL, создаем...")
            if not create_pg_table(pg_engine, table_name, sqlite_structure):
                return 0
        else:
            logger.info(f"Таблица {table_name} уже существует в PostgreSQL")
            
            # Проверяем наличие данных в таблице
            if not force:
                try:
                    with pg_engine.connect() as conn:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {quoted_table_name}"))
                        row_count = result.scalar()
                        if row_count > 0:
                            logger.warning(f"Таблица {table_name} уже содержит {row_count} строк, пропускаем... (используйте --force для принудительной миграции)")
                            return 0
                except Exception as e:
                    logger.error(f"Ошибка при проверке наличия данных в таблице {table_name}: {str(e)}")
                    return 0
            
            # Получаем структуру таблицы PostgreSQL
            pg_structure = get_pg_table_structure(pg_engine, table_name)
            
            # Добавляем отсутствующие столбцы
            add_missing_columns(pg_engine, table_name, sqlite_structure, pg_structure)
        
        # Считываем данные из SQLite
        logger.info(f"Чтение данных из таблицы {table_name}...")
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", sqlite_conn)
            logger.info(f"Считано {len(df)} строк из таблицы {table_name}")
            
            # Проверяем наличие данных
            if df.empty:
                logger.warning(f"Таблица {table_name} пуста, пропускаем...")
                return 0
        except Exception as e:
            logger.error(f"Ошибка при чтении данных из таблицы {table_name}: {str(e)}")
            return 0
        
        # Если таблица уже содержит данные и force=True, удаляем старые данные
        if force and table_exists:
            try:
                with pg_engine.connect() as conn:
                    conn.execute(text(f"DELETE FROM {quoted_table_name}"))
                    conn.commit()
                    logger.info(f"Существующие данные в таблице {table_name} удалены")
            except Exception as e:
                logger.error(f"Ошибка при удалении данных из таблицы {table_name}: {str(e)}")
                return 0
        
        # Получаем актуальную структуру таблицы PostgreSQL
        pg_structure = get_pg_table_structure(pg_engine, table_name)
        
        # Преобразуем типы данных
        df_converted = convert_data_types(df, pg_structure)
        
        # Выводим информацию о типах данных до и после преобразования
        logger.debug(f"Типы данных до преобразования: {df.dtypes}")
        logger.debug(f"Типы данных после преобразования: {df_converted.dtypes}")
        
        # Записываем данные в PostgreSQL
        logger.info(f"Запись {len(df_converted)} строк в PostgreSQL таблицу {table_name}...")
        try:
            # Преобразуем имя таблицы, если оно зарезервировано
            # При использовании to_sql с quoted_table_name возникают проблемы
            # с кавычками, поэтому используем оригинальное имя таблицы
            df_converted.to_sql(
                table_name,
                pg_engine,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=100,  # Меньший размер порции для отладки
                schema='public'  # Явно указываем схему
            )
            logger.info(f"Данные успешно записаны в таблицу {table_name}")
        except Exception as e:
            logger.error(f"Ошибка при записи данных в таблицу {table_name}: {str(e)}")
            logger.error(f"Столбцы DataFrame: {df_converted.columns.tolist()}")
            logger.error(f"Типы данных DataFrame: {df_converted.dtypes}")
            return 0
        
        # Обновляем последовательность (auto increment) в PostgreSQL
        if 'id' in df_converted.columns:
            max_id = df_converted['id'].max()
            if max_id:
                try:
                    with pg_engine.connect() as conn:
                        # Проверка существования последовательности
                        seq_name_query = text(
                            "SELECT pg_get_serial_sequence(:table_name, 'id') AS seq_name"
                        )
                        seq_name_result = conn.execute(seq_name_query, {"table_name": table_name}).fetchone()
                        
                        if seq_name_result and seq_name_result[0]:
                            seq_name = seq_name_result[0]
                            setval_query = text(f"SELECT setval('{seq_name}', :max_id)")
                            conn.execute(setval_query, {"max_id": max_id})
                            logger.info(f"Обновлена последовательность для таблицы {table_name} до значения {max_id}")
                except Exception as e:
                    logger.error(f"Ошибка при обновлении последовательности для таблицы {table_name}: {str(e)}")
        
        elapsed_time = time.time() - start_time
        logger.info(f"Таблица {table_name} успешно мигрирована за {elapsed_time:.2f} секунд!")
        return len(df_converted)
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Ошибка при миграции таблицы {table_name} после {elapsed_time:.2f} секунд: {str(e)}")
        return 0

def main():
    """Главная функция миграции"""
    parser = argparse.ArgumentParser(description='Миграция данных из SQLite в PostgreSQL')
    parser.add_argument('--force', action='store_true', help='Принудительная миграция таблиц, даже если они уже содержат данные')
    parser.add_argument('--tables', nargs='+', help='Список таблиц для миграции (по умолчанию все таблицы)')
    parser.add_argument('--skip-tables', nargs='+', help='Список таблиц, которые следует пропустить')
    parser.add_argument('--debug', action='store_true', help='Включить отладочное логирование')
    args = parser.parse_args()
    
    # Устанавливаем уровень логирования
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Включен режим отладки")
    
    start_time = time.time()
    logger.info("Начало миграции из SQLite в PostgreSQL...")
    
    # Создаем резервную копию SQLite
    backup_sqlite_db()
    
    # Создаем соединения с БД
    sqlite_conn, pg_engine = create_db_connections()
    
    try:
        # Получаем список таблиц
        all_tables = get_sqlite_tables(sqlite_conn)
        
        # Определяем таблицы для миграции
        if args.tables:
            tables = [t for t in args.tables if t in all_tables]
            if not tables:
                logger.error(f"Указанные таблицы не найдены в SQLite: {args.tables}")
                sys.exit(1)
        else:
            tables = all_tables
        
        # Исключаем таблицы, которые нужно пропустить
        if args.skip_tables:
            tables = [t for t in tables if t not in args.skip_tables]
            logger.info(f"Пропускаем таблицы: {args.skip_tables}")
        
        logger.info(f"Миграция {len(tables)} таблиц: {', '.join(tables)}")
        
        # Мигрируем каждую таблицу
        total_rows = 0
        successful_tables = 0
        failed_tables = []
        
        for table_name in tables:
            try:
                table_start_time = time.time()
                logger.info(f"Обработка таблицы {table_name}...")
                rows_migrated = migrate_table(sqlite_conn, pg_engine, table_name, force=args.force)
                table_elapsed_time = time.time() - table_start_time
                
                if rows_migrated > 0:
                    total_rows += rows_migrated
                    successful_tables += 1
                    logger.info(f"Успешно перенесено {rows_migrated} строк из таблицы {table_name} за {table_elapsed_time:.2f} секунд")
                else:
                    logger.warning(f"Таблица {table_name} не была перенесена (время: {table_elapsed_time:.2f} секунд)")
                    failed_tables.append(table_name)
            except Exception as e:
                logger.error(f"Непредвиденная ошибка при миграции таблицы {table_name}: {str(e)}")
                failed_tables.append(table_name)
        
        total_elapsed_time = time.time() - start_time
        logger.info(f"Миграция завершена за {total_elapsed_time:.2f} секунд!")
        logger.info(f"Перенесено {total_rows} строк из {successful_tables} таблиц.")
        
        if failed_tables:
            logger.warning(f"Не удалось перенести {len(failed_tables)} таблиц: {', '.join(failed_tables)}")
    except Exception as e:
        logger.error(f"Ошибка при миграции: {str(e)}")
    finally:
        sqlite_conn.close()
        logger.info("Соединения с базами данных закрыты.")

if __name__ == "__main__":
    main() 