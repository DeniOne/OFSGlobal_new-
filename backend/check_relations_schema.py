import sqlite3
import sys

def main():
    try:
        # Подключение к базе данных
        conn = sqlite3.connect('full_api_new.db')
        cursor = conn.cursor()
        
        with open('relations_schema.txt', 'w', encoding='utf-8') as file:
            # Запрос структуры таблицы
            cursor.execute('PRAGMA table_info(functional_relations)')
            columns = cursor.fetchall()
            
            file.write("=== Структура таблицы functional_relations ===\n")
            for column in columns:
                file.write(f"{column}\n")
            
            # Посмотрим, какие реально поля возвращаются при SELECT *
            cursor.execute('SELECT * FROM functional_relations LIMIT 1')
            
            # Если есть записи, выведем имена колонок и значения
            if cursor.rowcount > 0 or True:
                file.write("\n=== Колонки из SELECT * ===\n")
                column_names = [desc[0] for desc in cursor.description]
                file.write(f"{column_names}\n")
                
                rows = cursor.fetchall()
                if rows:
                    file.write("\n=== Пример данных ===\n")
                    for row in rows:
                        file.write(f"{row}\n")
                else:
                    file.write("\nТаблица не содержит записей\n")
            
            # Проверим, есть ли NOT NULL колонки
            file.write("\n=== NOT NULL колонки ===\n")
            cursor.execute("PRAGMA table_info(functional_relations)")
            for col in cursor.fetchall():
                col_name, col_type, not_null = col[1], col[2], col[3]
                if not_null:
                    file.write(f"{col_name} ({col_type}): NOT NULL = {not_null}\n")
                
        conn.close()
        print("Результаты сохранены в файл relations_schema.txt")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 