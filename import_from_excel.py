import pandas as pd
import psycopg2
import re
import sys
import os
from typing import Dict, List, Tuple, Optional

# Параметры подключения к базе данных
DB_PARAMS = {
    'dbname': 'ofs_db_new',
    'user': 'postgres',
    'password': 'QAZwsxr$t5',
    'host': 'localhost'
}

EXCEL_FILE = "ОФС стандартизированная полностью_v2.xlsx"

def clean_string(text: str) -> str:
    """Очистка строки от лишних символов"""
    if not isinstance(text, str):
        return ""
    return re.sub(r'\s+', ' ', str(text).strip())

def extract_name_from_title(title: str) -> str:
    """Извлечение имени из заголовка листа (например, из '1. ДЕПАРТАМЕНТ ПОСТРОЕНИЯ ОРГАНИЗАЦИИ')"""
    if not title:
        return ""
    
    # Удаление номера в начале
    clean_title = re.sub(r'^\d+\.?\s*', '', title)
    
    # Удаление слова "ДЕПАРТАМЕНТ"
    clean_title = re.sub(r'ДЕПАРТАМЕНТ\s+', '', clean_title)
    
    return clean_title.strip()

def connect_to_db():
    """Подключение к базе данных"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print(f"Успешное подключение к БД {DB_PARAMS['dbname']}")
        return conn
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        sys.exit(1)

def insert_organization(conn, name="ФОТОМАТРИЦА", ckp="Организация фотографического бизнеса"):
    """Создание основной организации в БД"""
    try:
        cur = conn.cursor()
        # Проверка, существует ли организация
        cur.execute("SELECT id FROM organizations WHERE name = %s", (name,))
        result = cur.fetchone()
        
        if result:
            print(f"Организация '{name}' уже существует с ID {result[0]}")
            return result[0]
        
        # Вставка новой организации
        cur.execute(
            "INSERT INTO organizations (name, description, is_active, org_type, ckp) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (name, "Головная организация", True, "holding", ckp)
        )
        org_id = cur.fetchone()[0]
        conn.commit()
        print(f"Создана организация '{name}' с ID {org_id}")
        return org_id
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при создании организации: {e}")
        return None

def insert_division(conn, org_id: int, name: str, ckp: str = None) -> Optional[int]:
    """Создание департамента в БД"""
    try:
        cur = conn.cursor()
        # Проверка, существует ли департамент
        cur.execute("SELECT id FROM divisions WHERE name = %s AND organization_id = %s", (name, org_id))
        result = cur.fetchone()
        
        if result:
            print(f"Департамент '{name}' уже существует с ID {result[0]}")
            return result[0]
        
        # Вставка нового департамента
        code = ''.join(word[0] for word in name.split() if word)
        cur.execute(
            "INSERT INTO divisions (name, code, organization_id, is_active, ckp) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (name, code, org_id, True, ckp)
        )
        div_id = cur.fetchone()[0]
        conn.commit()
        print(f"Создан департамент '{name}' с ID {div_id}")
        return div_id
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при создании департамента: {e}")
        return None

def insert_section(conn, division_id: int, name: str, ckp: str = None) -> Optional[int]:
    """Создание отдела в БД"""
    try:
        cur = conn.cursor()
        # Проверка, существует ли отдел
        cur.execute("SELECT id FROM sections WHERE name = %s AND division_id = %s", (name, division_id))
        result = cur.fetchone()
        
        if result:
            print(f"Отдел '{name}' уже существует с ID {result[0]}")
            return result[0]
        
        # Вставка нового отдела
        code = ''.join(word[0] for word in name.split() if word)
        cur.execute(
            "INSERT INTO sections (name, code, division_id, is_active, ckp) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (name, code, division_id, True, ckp)
        )
        section_id = cur.fetchone()[0]
        conn.commit()
        print(f"Создан отдел '{name}' с ID {section_id}")
        return section_id
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при создании отдела: {e}")
        return None

def insert_function(conn, section_id: int, name: str, ckp: str = None) -> Optional[int]:
    """Создание функции в БД"""
    try:
        cur = conn.cursor()
        # Проверка, существует ли функция
        cur.execute("SELECT id FROM functions WHERE name = %s AND section_id = %s", (name, section_id))
        result = cur.fetchone()
        
        if result:
            print(f"Функция '{name}' уже существует с ID {result[0]}")
            return result[0]
        
        # Вставка новой функции
        cur.execute(
            "INSERT INTO functions (name, section_id, is_active, ckp) VALUES (%s, %s, %s, %s) RETURNING id",
            (name, section_id, True, ckp)
        )
        function_id = cur.fetchone()[0]
        conn.commit()
        print(f"Создана функция '{name}' с ID {function_id}")
        return function_id
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при создании функции: {e}")
        return None

def process_department_sheet(conn, org_id: int, sheet_name: str, df: pd.DataFrame) -> None:
    """Обработка листа с департаментом"""
    dept_name = extract_name_from_title(sheet_name)
    print(f"\nОбработка департамента: {dept_name}")
    
    # Создаем департамент
    division_id = insert_division(conn, org_id, dept_name)
    if not division_id:
        return
    
    # Находим строки с отделами и их функциями
    section_pattern = re.compile(r'^\d+\.\d+\s+Отдел\s+', re.IGNORECASE)
    function_pattern = re.compile(r'^Функция', re.IGNORECASE)
    
    current_section_id = None
    
    for i in range(len(df)):
        row = df.iloc[i]
        
        # Проверяем первые 3 столбца на наличие данных
        col_values = [str(row.iloc[j]) for j in range(min(3, len(row))) if not pd.isna(row.iloc[j])]
        
        for value in col_values:
            if section_pattern.search(value):
                # Это отдел
                section_name = clean_string(value.split("Отдел")[1]) if "Отдел" in value else clean_string(value)
                current_section_id = insert_section(conn, division_id, section_name)
            elif function_pattern.search(value) and current_section_id:
                # Это функция
                function_name = clean_string(value)
                insert_function(conn, current_section_id, function_name)

def import_from_excel():
    """Импорт данных из Excel в БД"""
    if not os.path.exists(EXCEL_FILE):
        print(f"Файл {EXCEL_FILE} не найден!")
        return
    
    # Подключение к БД
    conn = connect_to_db()
    
    try:
        # Создание организации
        org_id = insert_organization(conn)
        if not org_id:
            return
        
        # Чтение Excel файла
        excel = pd.ExcelFile(EXCEL_FILE)
        sheet_names = excel.sheet_names
        
        # Обработка каждого листа департамента
        department_sheets = [sheet for sheet in sheet_names if re.search(r'^\d+\.?\s*ДЕПАРТАМЕНТ', sheet, re.IGNORECASE)]
        
        for sheet_name in department_sheets:
            df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
            process_department_sheet(conn, org_id, sheet_name, df)
        
        print("\nИмпорт завершен успешно!")
    
    except Exception as e:
        print(f"\nОшибка при импорте данных: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print(f"Запуск импорта данных из {EXCEL_FILE}...")
    import_from_excel() 