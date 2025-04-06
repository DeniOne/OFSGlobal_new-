import requests
import json

url = "http://localhost:8000/api/v1/organizations/"
data = {
    "name": "ОФС Глобал",
    "code": "OFS",
    "description": "Главная организация",
    "org_type": "holding",
    "is_active": True
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=data, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}") 