#!/usr/bin/env python

import os
import sqlite3
import argparse

def find_keys_in_db(db_path, search_pattern):
    """Ищет ключи с указанным шаблоном в базе данных."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Получаем все ключи из таблицы ItemTable
        cursor.execute("SELECT key FROM ItemTable WHERE key LIKE ?;", (f'%{search_pattern}%',))
        keys = cursor.fetchall()
        
        conn.close()
        
        if keys:
            print(f"\nНайдены ключи в {db_path}:")
            for key in keys:
                print(f"- {key[0]}")
            return len(keys)
        
        return 0
    except Exception as e:
        print(f"Ошибка при поиске ключей в {db_path}: {e}")
        return 0

def scan_dir_for_vscdb(base_path, search_pattern):
    """Сканирует директорию на наличие файлов .vscdb и ищет в них ключи."""
    total_found = 0
    
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith('.vscdb'):
                db_path = os.path.join(root, file)
                keys_found = find_keys_in_db(db_path, search_pattern)
                total_found += keys_found
    
    return total_found

def get_key_value(db_path, key_name):
    """Получает значение указанного ключа из базы данных."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM ItemTable WHERE key = ?;", (key_name,))
        value = cursor.fetchone()
        
        conn.close()
        
        if value:
            return value[0]
        
        return None
    except Exception as e:
        print(f"Ошибка при получении значения ключа {key_name} из {db_path}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Поиск ключей в базах данных Cursor')
    parser.add_argument('--path', default=os.path.join(os.environ.get('APPDATA', ''), 'Cursor', 'User', 'workspaceStorage'),
                        help='Путь для поиска файлов .vscdb')
    parser.add_argument('--search', help='Шаблон для поиска ключей (например, "chatdata")')
    parser.add_argument('--get-value', help='Получить значение конкретного ключа (используется с --db-path)')
    parser.add_argument('--db-path', help='Путь к конкретному файлу базы данных для --get-value')
    
    args = parser.parse_args()
    
    if args.get_value and args.db_path:
        value = get_key_value(args.db_path, args.get_value)
        if value:
            print(f"Значение ключа {args.get_value}:")
            print(value[:500] + '...' if len(value) > 500 else value)
        else:
            print(f"Ключ {args.get_value} не найден в {args.db_path}")
    elif args.search:
        print(f"Поиск ключей с шаблоном '{args.search}' в директории {args.path}")
        total = scan_dir_for_vscdb(args.path, args.search)
        print(f"\nВсего найдено ключей: {total}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 