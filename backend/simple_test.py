import requests
import json
import random
import string

# Конфигурация
API_URL = "http://127.0.0.1:8001"

def generate_random_string(length=5):
    """Генерирует случайную строку для создания уникальных кодов"""
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

def test_create_organization():
    """Тестирование создания организации-холдинга"""
    random_code = generate_random_string()
    holding_data = {
        "name": f"ОФС Глобал Холдинг {random_code}",
        "code": f"OFS-HOLDING-{random_code}",
        "description": "Головная компания холдинга",
        "org_type": "holding",
        "is_active": True,
        "inn": "7701234567",
        "kpp": "770101001",
        "legal_address": "г. Москва, ул. Ленина, д. 1",
        "ckp": "Управление группой компаний"
    }
    
    print("Создаем организацию-холдинг...")
    try:
        resp = requests.post(f"{API_URL}/organizations/", json=holding_data)
        print(f"Статус: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result["id"]  # Возвращаем ID для использования в других тестах
        else:
            print(f"Ошибка: {resp.text}")
            return None
    except Exception as e:
        print(f"Исключение: {str(e)}")
        return None

def test_create_legal_entity(parent_id):
    """Тестирование создания организации-юрлица"""
    if not parent_id:
        print("Ошибка: Не указан ID родительской организации")
        return
        
    random_code = generate_random_string()
    legal_entity_data = {
        "name": f"ООО Технологии будущего {random_code}",
        "code": f"TECH-{random_code}",
        "description": "Юридическое лицо для разработки",
        "org_type": "legal_entity",
        "is_active": True,
        "parent_id": parent_id,
        "inn": "7702345678",
        "kpp": "770201001",
        "legal_address": "г. Москва, ул. Гагарина, д. 10",
        "ckp": "Разработка программного обеспечения"
    }
    
    print("\nСоздаем организацию-юрлицо...")
    try:
        resp = requests.post(f"{API_URL}/organizations/", json=legal_entity_data)
        print(f"Статус: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result["id"]
        else:
            print(f"Ошибка: {resp.text}")
            return None
    except Exception as e:
        print(f"Исключение: {str(e)}")
        return None

def test_create_division(organization_id):
    """Тестирование создания подразделения"""
    if not organization_id:
        print("Ошибка: Не указан ID организации")
        return
    
    random_code = generate_random_string()
    division_data = {
        "name": f"Департамент разработки {random_code}",
        "code": f"DEV-{random_code}",
        "description": "Департамент разработки программного обеспечения",
        "is_active": True,
        "organization_id": organization_id,
        "ckp": "Разработка внутренних и внешних продуктов"
    }
    
    print("\nСоздаем подразделение...")
    try:
        resp = requests.post(f"{API_URL}/divisions/", json=division_data)
        print(f"Статус: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result["id"]
        else:
            print(f"Ошибка: {resp.text}")
            return None
    except Exception as e:
        print(f"Исключение: {str(e)}")
        return None

def test_create_section():
    """Тестирование создания отдела"""
    random_code = generate_random_string()
    section_data = {
        "name": f"Отдел веб-разработки {random_code}",
        "code": f"WEB-DEV-{random_code}",
        "description": "Отдел веб-разработки",
        "is_active": True,
        "ckp": "Создание и поддержка веб-приложений"
    }
    
    print("\nСоздаем отдел...")
    try:
        resp = requests.post(f"{API_URL}/sections/", json=section_data)
        print(f"Статус: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result["id"]
        else:
            print(f"Ошибка: {resp.text}")
            return None
    except Exception as e:
        print(f"Исключение: {str(e)}")
        return None

def test_link_division_section(division_id, section_id):
    """Тестирование связывания подразделения и отдела"""
    if not division_id or not section_id:
        print("Ошибка: Не указан ID подразделения или отдела")
        return
        
    link_data = {
        "division_id": division_id,
        "section_id": section_id,
        "is_primary": True
    }
    
    print("\nСвязываем подразделение и отдел...")
    try:
        resp = requests.post(f"{API_URL}/division-sections/", json=link_data)
        print(f"Статус: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result["id"]
        else:
            print(f"Ошибка: {resp.text}")
            return None
    except Exception as e:
        print(f"Исключение: {str(e)}")
        return None

def test_create_function():
    """Тестирование создания функции"""
    random_code = generate_random_string()
    function_data = {
        "name": f"Разработка программного обеспечения {random_code}",
        "code": f"SOFTWARE-DEV-{random_code}",
        "description": "Разработка и сопровождение программного обеспечения",
        "is_active": True
    }
    
    print("\nСоздаем функцию...")
    try:
        resp = requests.post(f"{API_URL}/functions/", json=function_data)
        print(f"Статус: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result["id"]
        else:
            print(f"Ошибка: {resp.text}")
            return None
    except Exception as e:
        print(f"Исключение: {str(e)}")
        return None

def test_link_section_function(section_id, function_id):
    """Тестирование связывания отдела и функции"""
    if not section_id or not function_id:
        print("Ошибка: Не указан ID отдела или функции")
        return
        
    link_data = {
        "section_id": section_id,
        "function_id": function_id,
        "is_primary": True
    }
    
    print("\nСвязываем отдел и функцию...")
    try:
        resp = requests.post(f"{API_URL}/section-functions/", json=link_data)
        print(f"Статус: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result["id"]
        else:
            print(f"Ошибка: {resp.text}")
            return None
    except Exception as e:
        print(f"Исключение: {str(e)}")
        return None

def test_create_position(function_id):
    """Тестирование создания должности"""
    if not function_id:
        print("Ошибка: Не указан ID функции")
        return
    
    random_code = generate_random_string()
    position_data = {
        "name": f"Старший разработчик {random_code}",
        "code": f"SENIOR-DEV-{random_code}",
        "description": "Старший разработчик с опытом работы от 3 лет",
        "is_active": True,
        "function_id": function_id
    }
    
    print("\nСоздаем должность...")
    try:
        resp = requests.post(f"{API_URL}/positions/", json=position_data)
        print(f"Статус: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result["id"]
        else:
            print(f"Ошибка: {resp.text}")
            return None
    except Exception as e:
        print(f"Исключение: {str(e)}")
        return None

def test_create_staff(organization_id):
    """Тестирование создания сотрудника"""
    if not organization_id:
        print("Ошибка: Не указан ID организации")
        return
    
    random_code = generate_random_string()
    staff_data = {
        "email": f"ivanov{random_code.lower()}@example.com",
        "first_name": "Иван",
        "last_name": f"Иванов {random_code}",
        "middle_name": "Иванович",
        "phone": "+7 (999) 123-45-67",
        "description": "Опытный разработчик",
        "is_active": True,
        "organization_id": organization_id
    }
    
    print("\nСоздаем сотрудника...")
    try:
        resp = requests.post(f"{API_URL}/staff/", json=staff_data)
        print(f"Статус: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result["id"]
        else:
            print(f"Ошибка: {resp.text}")
            return None
    except Exception as e:
        print(f"Исключение: {str(e)}")
        return None

def test_assign_position(staff_id, position_id):
    """Тестирование назначения должности сотруднику"""
    if not staff_id or not position_id:
        print("Ошибка: Не указан ID сотрудника или должности")
        return
        
    assign_data = {
        "staff_id": staff_id,
        "position_id": position_id,
        "is_primary": True,
        "is_active": True,
        "start_date": "2025-03-31"
    }
    
    print("\nНазначаем должность сотруднику...")
    try:
        resp = requests.post(f"{API_URL}/staff-positions/", json=assign_data)
        print(f"Статус: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result["id"]
        else:
            print(f"Ошибка: {resp.text}")
            return None
    except Exception as e:
        print(f"Исключение: {str(e)}")
        return None

if __name__ == "__main__":
    # Проверяем доступность API
    try:
        resp = requests.get(f"{API_URL}/")
        if resp.status_code == 200:
            print(f"API доступен: {resp.json()}")
            # Выполняем тесты по порядку с проверкой результатов на каждом шаге
            
            # 1. Создаем холдинг (основную организацию)
            holding_id = test_create_organization()
            
            if holding_id:
                # 2. Создаем юридическое лицо внутри холдинга
                legal_entity_id = test_create_legal_entity(holding_id)
                
                # 3. Создаем подразделение в холдинге
                division_id = test_create_division(holding_id)
                
                # 4. Создаем отдел
                section_id = test_create_section()
                
                # 5. Связываем подразделение и отдел
                if division_id and section_id:
                    div_section_id = test_link_division_section(division_id, section_id)
                
                # 6. Создаем функцию
                function_id = test_create_function()
                
                # 7. Связываем отдел и функцию
                if section_id and function_id:
                    section_function_id = test_link_section_function(section_id, function_id)
                
                # 8. Создаем должность на основе функции
                if function_id:
                    position_id = test_create_position(function_id)
                
                # 9. Создаем сотрудника в юридическом лице (не в холдинге)
                if legal_entity_id:
                    staff_id = test_create_staff(legal_entity_id)
                    
                    # 10. Назначаем должность сотруднику
                    if staff_id and position_id:
                        staff_position_id = test_assign_position(staff_id, position_id)
                        
                # Выводим результаты        
                print("\n=== Результаты тестирования ===")
                print(f"Создана организация-холдинг с ID: {holding_id}")
                print(f"Создана организация-юрлицо с ID: {legal_entity_id}")
                print(f"Создано подразделение с ID: {division_id}")
                print(f"Создан отдел с ID: {section_id}")
                print(f"Создана функция с ID: {function_id}")
                print(f"Создана должность с ID: {position_id}")
                print(f"Создан сотрудник с ID: {staff_id}")
        else:
            print(f"API недоступен. Статус: {resp.status_code}")
    except Exception as e:
        print(f"Ошибка при подключении к API: {str(e)}") 