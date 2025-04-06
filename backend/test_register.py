import requests
import json

# Данные для регистрации
data = {
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User"
}

# URL-адрес для регистрации напрямую
url = "http://localhost:8000/api/register"

print("🔥 Тест отправки запроса на регистрацию")
print(f"📌 URL: {url}")
print(f"📌 Данные: {data}")

# Отправляем POST-запрос
try:
    response = requests.post(
        url,
        json=data,  # Автоматически конвертирует в JSON и устанавливает Content-Type
        headers={"Accept": "application/json"}
    )
    
    # Выводим результат
    print(f"📌 Код ответа: {response.status_code}")
    print(f"📌 Тело ответа: {response.text}")
    
    # Проверяем успешность регистрации
    if response.status_code == 201:
        print("✅ Регистрация успешно выполнена!")
    else:
        print("❌ Ошибка при регистрации!")
        
except Exception as e:
    print(f"❌ Исключение: {str(e)}") 