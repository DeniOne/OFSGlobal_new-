#!/usr/bin/env python
import os
import sqlite3
import json
import argparse

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
    parser = argparse.ArgumentParser(description='Экспорт значения ключа из базы данных в файл JSON')
    parser.add_argument('--db-path', required=True, help='Путь к файлу базы данных')
    parser.add_argument('--key', required=True, help='Имя ключа для экспорта')
    parser.add_argument('--output', required=True, help='Имя файла для сохранения результата')
    
    args = parser.parse_args()
    
    value = get_key_value(args.db_path, args.key)
    if value:
        try:
            # Пытаемся распарсить как JSON
            data = json.loads(value)
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Значение ключа {args.key} успешно сохранено в файл {args.output}")
        except json.JSONDecodeError:
            # Если не получилось распарсить как JSON, сохраняем как текст
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(value)
            print(f"Значение ключа {args.key} сохранено как текст в файл {args.output}")
    else:
        print(f"Ключ {args.key} не найден в {args.db_path}")

if __name__ == "__main__":
    main() 