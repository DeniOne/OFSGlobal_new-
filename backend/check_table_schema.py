import sqlite3
import sys

def main():
    try:
        # Подключение к базе данных
        conn = sqlite3.connect('full_api_new.db')
        cursor = conn.cursor()
        
        # Запрос структуры таблицы
        cursor.execute('PRAGMA table_info(functional_relations)')
        columns = cursor.fetchall()
        
        # Запись результатов в файл
        with open('table_schema.txt', 'w', encoding='utf-8') as file:
            file.write("Структура таблицы functional_relations:\n")
            for column in columns:
                file.write(f"{column}\n")
            
            # Получим также несколько записей из таблицы, если они есть
            cursor.execute('SELECT * FROM functional_relations LIMIT 5')
            rows = cursor.fetchall()
            
            if rows:
                file.write("\nПримеры записей:\n")
                for row in rows:
                    file.write(f"{row}\n")
            else:
                file.write("\nТаблица не содержит записей\n")
                
        conn.close()
        print("Результаты сохранены в файл table_schema.txt")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 