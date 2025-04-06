"""
Скрипт для тестирования полного API и заполнения его тестовыми данными
"""
import os
import sqlite3
import requests
import json
from datetime import datetime, date, timedelta

# Конфигурация
API_URL = "http://127.0.0.1:8001"
DB_PATH = "full_api.db"

# Удаление существующей базы данных, чтобы начать с чистого листа
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print(f"Удалена существующая база данных: {DB_PATH}")

def print_response(resp, operation):
    """Вывод ответа API для отладки"""
    print(f"\n{operation} - Статус: {resp.status_code}")
    if resp.status_code == 200:
        try:
            print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
        except:
            print(resp.text)
    else:
        print(f"Ошибка: {resp.text}")

def create_test_data():
    """Создание тестовых данных через API"""
    
    # 1. Создаем организации
    print("\n=== СОЗДАЕМ ОРГАНИЗАЦИИ ===")
    
    # Создаем HOLDING
    holding_data = {
        "name": "ОФС Глобал Холдинг",
        "code": "OFS-HOLDING",
        "description": "Головная компания холдинга",
        "org_type": "holding",
        "is_active": True,
        "inn": "7701234567",
        "kpp": "770101001",
        "legal_address": "г. Москва, ул. Ленина, д. 1",
        "ckp": "Управление группой компаний"
    }
    resp = requests.post(f"{API_URL}/organizations/", json=holding_data)
    print_response(resp, "Создание HOLDING")
    holding_id = resp.json()["id"]
    
    # Создаем юридическое лицо (ООО)
    legal_entity_data = {
        "name": "ООО ОФС Технологии",
        "code": "OFS-TECH",
        "description": "Технологическое подразделение",
        "org_type": "legal_entity",
        "parent_id": holding_id, 
        "is_active": True,
        "inn": "7702345678",
        "kpp": "770201001",
        "legal_address": "г. Москва, ул. Пушкина, д. 10",
        "ckp": "Технологические решения"
    }
    resp = requests.post(f"{API_URL}/organizations/", json=legal_entity_data)
    print_response(resp, "Создание LEGAL_ENTITY")
    legal_entity_id = resp.json()["id"]
    
    # Создаем физическую локацию (офис)
    location_data = {
        "name": "Офис Москва-Сити",
        "code": "MSK-CITY",
        "description": "Главный офис в Москва-Сити",
        "org_type": "location",
        "parent_id": legal_entity_id,
        "is_active": True,
        "physical_address": "г. Москва, Пресненская наб., д. 12, Башня Федерация",
        "ckp": "Центральный офис"
    }
    resp = requests.post(f"{API_URL}/organizations/", json=location_data)
    print_response(resp, "Создание LOCATION")
    location_id = resp.json()["id"]
    
    # 2. Получаем список организаций
    print("\n=== ПОЛУЧАЕМ СПИСОК ОРГАНИЗАЦИЙ ===")
    resp = requests.get(f"{API_URL}/organizations/")
    print_response(resp, "Получение списка организаций")
    
    # Получаем организации типа HOLDING
    resp = requests.get(f"{API_URL}/organizations/?org_type=holding")
    print_response(resp, "Получение организаций типа HOLDING")
    
    # Получаем дочерние организации для холдинга
    resp = requests.get(f"{API_URL}/organizations/?parent_id={holding_id}")
    print_response(resp, "Получение дочерних организаций холдинга")
    
    # 3. Прямой доступ к базе данных для создания всех остальных данных
    print("\n=== ДОБАВЛЯЕМ ОСТАЛЬНЫЕ ДАННЫЕ НАПРЯМУЮ В БАЗУ ===")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Создаем Division (Подразделение)
        cursor.execute("""
            INSERT INTO divisions (name, code, description, is_active, organization_id, ckp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("ИТ Подразделение", "IT-DIV", "Подразделение информационных технологий", 1, holding_id, "Разработка и поддержка ПО"))
        division_id = cursor.lastrowid
        print(f"Создано подразделение с ID: {division_id}")
        
        # Создаем Section (Отдел)
        cursor.execute("""
            INSERT INTO sections (name, code, description, is_active, ckp)
            VALUES (?, ?, ?, ?, ?)
        """, ("Отдел разработки", "DEV", "Отдел разработки программного обеспечения", 1, "Разработка новых продуктов"))
        section_id = cursor.lastrowid
        print(f"Создан отдел с ID: {section_id}")
        
        # Связываем Division и Section
        cursor.execute("""
            INSERT INTO division_sections (division_id, section_id, is_primary)
            VALUES (?, ?, ?)
        """, (division_id, section_id, 1))
        print(f"Создана связь между подразделением {division_id} и отделом {section_id}")
        
        # Создаем Function (Функция)
        cursor.execute("""
            INSERT INTO functions (name, code, description, is_active)
            VALUES (?, ?, ?, ?)
        """, ("Backend разработка", "BACKEND", "Разработка серверной части приложений", 1))
        function_id = cursor.lastrowid
        print(f"Создана функция с ID: {function_id}")
        
        # Связываем Section и Function
        cursor.execute("""
            INSERT INTO section_functions (section_id, function_id, is_primary)
            VALUES (?, ?, ?)
        """, (section_id, function_id, 1))
        print(f"Создана связь между отделом {section_id} и функцией {function_id}")
        
        # Создаем Position (Должность)
        cursor.execute("""
            INSERT INTO positions (name, code, description, is_active, function_id)
            VALUES (?, ?, ?, ?, ?)
        """, ("Senior Backend Developer", "SR-BACKEND", "Старший разработчик серверной части", 1, function_id))
        position_id = cursor.lastrowid
        print(f"Создана должность с ID: {position_id}")
        
        # Создаем Staff (Сотрудник)
        cursor.execute("""
            INSERT INTO staff (email, first_name, last_name, middle_name, phone, description, is_active, organization_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("ivanov@example.com", "Иван", "Иванов", "Петрович", "+7 (999) 123-45-67", "Ведущий разработчик", 1, legal_entity_id))
        staff_id = cursor.lastrowid
        print(f"Создан сотрудник с ID: {staff_id}")
        
        # Связываем Staff и Position
        cursor.execute("""
            INSERT INTO staff_positions (staff_id, position_id, location_id, is_primary, is_active, start_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (staff_id, position_id, location_id, 1, 1, date.today().isoformat()))
        print(f"Создана связь между сотрудником {staff_id} и должностью {position_id}")
        
        # Связываем Staff и Function
        cursor.execute("""
            INSERT INTO staff_functions (staff_id, function_id, is_supervisor, description, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, (staff_id, function_id, 1, "Руководитель направления бэкенд-разработки", 1))
        print(f"Создана связь между сотрудником {staff_id} и функцией {function_id}")
        
        # Создаем еще одного сотрудника для демонстрации функциональных отношений
        cursor.execute("""
            INSERT INTO staff (email, first_name, last_name, middle_name, phone, description, is_active, organization_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("petrov@example.com", "Петр", "Петров", "Иванович", "+7 (999) 987-65-43", "Разработчик", 1, legal_entity_id))
        staff_id2 = cursor.lastrowid
        print(f"Создан сотрудник 2 с ID: {staff_id2}")
        
        # Связываем второго сотрудника с должностью (той же)
        cursor.execute("""
            INSERT INTO staff_positions (staff_id, position_id, location_id, is_primary, is_active, start_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (staff_id2, position_id, location_id, 1, 1, date.today().isoformat()))
        print(f"Создана связь между сотрудником {staff_id2} и должностью {position_id}")
        
        # Создаем функциональное отношение между сотрудниками
        cursor.execute("""
            INSERT INTO functional_relations (manager_id, subordinate_id, relation_type, description, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, (staff_id, staff_id2, "functional", "Функциональное подчинение", 1))
        print(f"Создано функциональное отношение между руководителем {staff_id} и подчиненным {staff_id2}")
        
        conn.commit()
        print("Все тестовые данные успешно добавлены в базу")
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при создании тестовых данных: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Проверяем доступность API
    try:
        resp = requests.get(f"{API_URL}/")
        if resp.status_code == 200:
            print(f"API доступен: {resp.json()}")
            # Создаем тестовые данные
            create_test_data()
        else:
            print(f"API недоступен. Статус: {resp.status_code}")
    except Exception as e:
        print(f"Ошибка при подключении к API: {str(e)}")
        print("Убедитесь, что сервер API запущен с помощью 'python full_api.py'") 