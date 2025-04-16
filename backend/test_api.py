#!/usr/bin/env python
"""
Скрипт для проверки API без использования PowerShell
"""
import requests
import json

def main():
    # Проверяем корневой URL
    base_url = "http://localhost:8001"
    print(f"Отправляем GET запрос на {base_url}")
    
    try:
        # Отправка запроса
        response = requests.get(base_url)
        
        # Вывод статуса
        print(f"Статус ответа: {response.status_code}")
        print(f"Заголовки: {response.headers}")
        
        # Вывод содержимого
        if response.status_code == 200:
            print("\nСодержимое ответа:")
            print(response.text)
            
            # Попытка разбора JSON
            try:
                data = response.json()
                print("\nРазобранный JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"\nОшибка при разборе JSON: {e}")
    
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
    
    # Проверяем URL организаций
    api_url = f"{base_url}/api/v1/organizations/"
    print(f"\nОтправляем GET запрос на {api_url}")
    
    try:
        # Отправка запроса
        response = requests.get(api_url)
        
        # Вывод статуса
        print(f"Статус ответа: {response.status_code}")
        print(f"Заголовки: {response.headers}")
        
        # Вывод содержимого
        if response.status_code == 200:
            print("\nСодержимое ответа:")
            print(response.text)
            
            # Попытка разбора JSON
            try:
                data = response.json()
                print("\nРазобранный JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"\nОшибка при разборе JSON: {e}")
    
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")

if __name__ == "__main__":
    main() 