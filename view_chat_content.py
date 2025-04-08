#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple script to view chat content from a Cursor SQLite database
"""

import sqlite3
import json
import sys
import os
import argparse
from pathlib import Path

def find_vscdb_files(base_path):
    """Находит все файлы state.vscdb в указанной директории и поддиректориях."""
    vscdb_files = []
    for root, _, files in os.walk(base_path):
        if 'state.vscdb' in files:
            vscdb_path = os.path.join(root, 'state.vscdb')
            vscdb_files.append((vscdb_path, os.path.getmtime(vscdb_path)))
    
    # Сортировка по времени изменения (новые вверху)
    vscdb_files.sort(key=lambda x: x[1], reverse=True)
    
    return [path for path, _ in vscdb_files]

def list_all_tables(db_path):
    """Выводит список всех таблиц в базе данных."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Запрос для получения списка всех таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        conn.close()
        
        return [table[0] for table in tables]
    except Exception as e:
        print(f"Ошибка при чтении таблиц из базы данных {db_path}: {e}")
        return []

def list_table_columns(db_path, table_name):
    """Выводит список столбцов таблицы."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Запрос для получения информации о столбцах таблицы
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        conn.close()
        
        return [column[1] for column in columns]
    except Exception as e:
        print(f"Ошибка при чтении столбцов таблицы {table_name} из базы данных {db_path}: {e}")
        return []

def query_item_table(db_path):
    """Запрашивает данные из таблицы ItemTable."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Запрос для получения всех ключей из таблицы ItemTable
        cursor.execute("SELECT key FROM ItemTable;")
        keys = cursor.fetchall()
        
        # Выводим все ключи
        all_keys = [key[0] for key in keys]
        print(f"Всего найдено {len(all_keys)} ключей")
        
        # Ищем ключи, связанные с чатом
        chat_keys = [key for key in all_keys if 'chat' in key.lower()]
        print("\nКлючи, связанные с чатом:")
        for key in chat_keys:
            print(f"- {key}")
        
        # Запрашиваем значения для ключей, связанных с чатом
        chat_data = {}
        for key in chat_keys:
            cursor.execute("SELECT value FROM ItemTable WHERE key = ?;", (key,))
            value = cursor.fetchone()
            if value and value[0]:
                try:
                    # Пробуем распарсить как JSON
                    chat_data[key] = json.loads(value[0])
                except:
                    # Если не получилось, сохраняем как строку
                    chat_data[key] = value[0]
        
        conn.close()
        
        return chat_data
    except Exception as e:
        print(f"Ошибка при запросе данных из таблицы ItemTable базы данных {db_path}: {e}")
        return {}

def dump_chat_data(chat_data, output_file=None):
    """Выводит или сохраняет данные чатов."""
    if not chat_data:
        print("Данные чатов не найдены.")
        return
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
        print(f"Данные чатов сохранены в файл: {output_file}")
    else:
        print("\nДанные чатов:")
        print(json.dumps(chat_data, ensure_ascii=False, indent=2))

def main():
    parser = argparse.ArgumentParser(description='Инструмент для просмотра содержимого чатов Cursor')
    parser.add_argument('--workspace-dir', default=os.path.join(os.environ.get('APPDATA', ''), 'Cursor', 'User', 'workspaceStorage'),
                        help='Путь к директории с рабочими пространствами Cursor')
    parser.add_argument('--db-path', help='Прямой путь к файлу state.vscdb')
    parser.add_argument('--output', help='Путь для сохранения данных чатов в JSON-файл')
    parser.add_argument('--list-tables', action='store_true', help='Вывести список всех таблиц в базе данных')
    parser.add_argument('--list-columns', help='Вывести список столбцов для указанной таблицы')
    parser.add_argument('--list-workspaces', action='store_true', help='Вывести список всех рабочих пространств')
    
    args = parser.parse_args()
    
    if args.list_workspaces:
        print("Список всех рабочих пространств:")
        workspaces = os.listdir(args.workspace_dir)
        for workspace in workspaces:
            workspace_path = os.path.join(args.workspace_dir, workspace)
            if os.path.isdir(workspace_path):
                print(f"- {workspace}")
        return
    
    if args.db_path:
        db_files = [args.db_path]
    else:
        print(f"Поиск файлов state.vscdb в директории: {args.workspace_dir}")
        db_files = find_vscdb_files(args.workspace_dir)
        
    if not db_files:
        print("Файлы state.vscdb не найдены.")
        return
    
    print(f"Найдено {len(db_files)} файлов state.vscdb:")
    for i, db_file in enumerate(db_files):
        print(f"{i+1}. {db_file}")
    
    if args.list_tables:
        # Вывести список таблиц для первого файла
        db_path = db_files[0]
        print(f"\nТаблицы в базе данных {db_path}:")
        tables = list_all_tables(db_path)
        for table in tables:
            print(f"- {table}")
        return
    
    if args.list_columns:
        # Вывести список столбцов для указанной таблицы в первом файле
        db_path = db_files[0]
        print(f"\nСтолбцы таблицы {args.list_columns} в базе данных {db_path}:")
        columns = list_table_columns(db_path, args.list_columns)
        for column in columns:
            print(f"- {column}")
        return
    
    # Запросить данные из первого файла
    db_path = db_files[0]
    print(f"\nЗапрос данных из базы данных {db_path}:")
    chat_data = query_item_table(db_path)
    dump_chat_data(chat_data, args.output)

if __name__ == "__main__":
    main()
    print("\nPress Enter to exit...")
    input() 