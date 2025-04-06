import requests
import json

# Создаем тестовый ЦКП
data = {
    "entity_type": "board",
    "entity_id": 1,
    "name": "Стратегическое развитие",
    "description": "Разработка и внедрение стратегии развития компании",
    "metrics": {
        "roi": "15%",
        "market_share": "25%"
    },
    "status": "in_progress",
    "progress": 30
}

# Отправляем POST запрос
response = requests.post(
    "http://localhost:8001/vfp/",
    json=data
)

# Выводим результат
print(f"Status code: {response.status_code}")
print("Response:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False)) 