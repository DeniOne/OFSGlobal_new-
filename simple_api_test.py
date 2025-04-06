import requests
import json

# Базовый URL API
API_URL = "http://127.0.0.1:8000"
API_PREFIX = "/api/v1"  # Важный префикс!

def test_api():
    # Проверка доступности сервера
    print("🔍 Проверка доступности API...")
    try:
        response = requests.get(f"{API_URL}/")
        print(f"  Корневой URL: статус {response.status_code}")
        if response.status_code == 200:
            print(f"  Ответ: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при подключении к серверу: {str(e)}")
        return
    
    # Проверка документации API
    try:
        response = requests.get(f"{API_URL}/docs")
        print(f"  Документация API: статус {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка при доступе к документации: {str(e)}")
    
    # Проверка эндпоинта организаций
    try:
        print("\n🔍 Проверка эндпоинта организаций...")
        response = requests.get(f"{API_URL}{API_PREFIX}/organizations/")
        print(f"  GET {API_PREFIX}/organizations/: статус {response.status_code}")
        if response.status_code == 200:
            print(f"  Организации: {response.text[:200]}...")
        else:
            print(f"  Ошибка: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при запросе организаций: {str(e)}")
    
    # Пробуем создать организацию
    try:
        print("\n🔍 Попытка создания организации...")
        org_data = {
            "name": "Тестовая организация",
            "code": "test_org",
            "description": "Тестовая организация для проверки API",
            "org_type": "legal_entity",
            "is_active": True,
            "inn": "7701234567",
            "kpp": "770101001",
            "legal_address": "Тестовый адрес",
            "physical_address": "Тестовый адрес"
        }
        
        response = requests.post(f"{API_URL}{API_PREFIX}/organizations/", json=org_data)
        print(f"  POST {API_PREFIX}/organizations/: статус {response.status_code}")
        if response.status_code in (200, 201):
            print(f"  Успешно создана организация: {response.text[:200]}...")
        else:
            print(f"  Ошибка: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при создании организации: {str(e)}")
    
    # Проверка эндпоинта подразделений (divisions)
    try:
        print("\n🔍 Проверка эндпоинта подразделений...")
        response = requests.get(f"{API_URL}{API_PREFIX}/divisions/")
        print(f"  GET {API_PREFIX}/divisions/: статус {response.status_code}")
        if response.status_code == 200:
            print(f"  Подразделения: {response.text[:200]}...")
        else:
            print(f"  Ошибка: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при запросе подразделений: {str(e)}")
    
    # Проверка эндпоинта сотрудников (staff)
    try:
        print("\n🔍 Проверка эндпоинта сотрудников...")
        response = requests.get(f"{API_URL}{API_PREFIX}/staff/")
        print(f"  GET {API_PREFIX}/staff/: статус {response.status_code}")
        if response.status_code == 200:
            print(f"  Сотрудники: {response.text[:200]}...")
        else:
            print(f"  Ошибка: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при запросе сотрудников: {str(e)}")

if __name__ == "__main__":
    test_api() 