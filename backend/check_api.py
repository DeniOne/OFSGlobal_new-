#!/usr/bin/env python
"""
Скрипт для проверки работы API с новой базой данных.
"""

import requests
import json
from pprint import pprint
import time

BASE_URL = "http://127.0.0.1:8080"

def check_endpoint(endpoint, method="GET", data=None, params=None):
    """
    Выполняет запрос к эндпоинту API и выводит результат.
    
    Args:
        endpoint (str): Путь к эндпоинту API.
        method (str): HTTP метод (GET, POST, PUT, DELETE).
        data (dict): Данные для запроса (для POST, PUT).
        params (dict): Параметры запроса (для GET).
    """
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*80}")
    print(f"Запрос: {method} {url}")
    
    if params:
        print(f"Параметры: {params}")
    
    if data:
        print(f"Данные: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            print(f"Неподдерживаемый метод: {method}")
            return
        
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 204:
            print("Нет содержимого (No Content)")
            return True
        
        if response.text:
            try:
                response_data = response.json()
                print("Ответ:")
                pprint(response_data, width=100, sort_dicts=False)
                return response_data
            except json.JSONDecodeError:
                print("Ответ не является JSON:")
                print(response.text)
        else:
            print("Пустой ответ")
        
        return response.status_code < 400  # True если успешный запрос
        
    except requests.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return False

def main():
    print("Проверка API на новой базе данных...")
    
    # Проверка основного маршрута
    check_endpoint("/")
    
    # 1. Проверка получения организаций
    print("\n=== ПРОВЕРКА ОРГАНИЗАЦИЙ ===")
    organizations = check_endpoint("/organizations/")
    
    # 2. Проверка получения подразделений
    print("\n=== ПРОВЕРКА ПОДРАЗДЕЛЕНИЙ ===")
    divisions = check_endpoint("/divisions/")
    
    # 3. Проверка получения подразделений по организации
    if organizations and len(organizations) > 0:
        org_id = organizations[0]["id"]
        print(f"\n=== ПРОВЕРКА ПОДРАЗДЕЛЕНИЙ ПО ОРГАНИЗАЦИИ (ID: {org_id}) ===")
        check_endpoint("/divisions/", params={"organization_id": org_id})
    
    # 4. Проверка получения сотрудников
    print("\n=== ПРОВЕРКА СОТРУДНИКОВ ===")
    staff = check_endpoint("/staff/")
    
    # 5. Проверка получения сотрудника по ID
    if staff and len(staff) > 0:
        staff_id = staff[0]["id"]
        print(f"\n=== ПРОВЕРКА СОТРУДНИКА ПО ID (ID: {staff_id}) ===")
        check_endpoint(f"/staff/{staff_id}")
    
    # 6. Проверка получения должностей
    print("\n=== ПРОВЕРКА ДОЛЖНОСТЕЙ ===")
    positions = check_endpoint("/positions/")
    
    # 7. Проверка получения должностей сотрудника
    if staff and len(staff) > 0:
        staff_id = staff[0]["id"]
        print(f"\n=== ПРОВЕРКА ДОЛЖНОСТЕЙ СОТРУДНИКА (ID: {staff_id}) ===")
        check_endpoint("/staff-positions/", params={"staff_id": staff_id})
    
    # 8. Проверка получения локаций сотрудника
    if staff and len(staff) > 0:
        staff_id = staff[0]["id"]
        print(f"\n=== ПРОВЕРКА ЛОКАЦИЙ СОТРУДНИКА (ID: {staff_id}) ===")
        check_endpoint("/staff-locations/", params={"staff_id": staff_id})
    
    # 9. Проверка функциональных отношений
    print("\n=== ПРОВЕРКА ФУНКЦИОНАЛЬНЫХ ОТНОШЕНИЙ ===")
    relations = check_endpoint("/functional-relations/")
    
    # 10. Проверка создания нового сотрудника
    print("\n=== ПРОВЕРКА СОЗДАНИЯ СОТРУДНИКА ===")
    new_staff_data = {
        "email": f"test.user.{int(time.time())}@example.com",
        "first_name": "Тестовый",
        "last_name": "Пользователь",
        "phone": "+7 999 123-45-67",
        "is_active": True,
    }
    new_staff = check_endpoint("/staff/", method="POST", data=new_staff_data)
    
    # 11. Если сотрудник создан, проверяем назначение ему должности
    if new_staff and isinstance(new_staff, dict) and "id" in new_staff:
        staff_id = new_staff["id"]
        
        # Берем первую найденную должность
        if positions and len(positions) > 0:
            position_id = positions[0]["id"]
            
            # Берем первое найденное подразделение
            division_id = divisions[0]["id"] if divisions and len(divisions) > 0 else None
            
            print(f"\n=== НАЗНАЧЕНИЕ ДОЛЖНОСТИ СОТРУДНИКУ (ID: {staff_id}) ===")
            staff_position_data = {
                "staff_id": staff_id,
                "position_id": position_id,
                "division_id": division_id,
                "is_primary": True,
                "is_active": True,
                "start_date": "2023-05-01"
            }
            check_endpoint("/staff-positions/", method="POST", data=staff_position_data)

    print("\nПроверка API завершена.")

if __name__ == "__main__":
    main() 