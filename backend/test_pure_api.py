import requests
import json

url = "http://localhost:8001/organizations/"
data = {
    "name": "ОФС Глобал API",
    "code": "OFSAPI",
    "description": "Тестовая организация через чистый API",
    "org_type": "holding",
    "is_active": True
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=data, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}") 