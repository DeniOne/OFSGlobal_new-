import requests
import json

url = "http://localhost:8000/api/v1/test-create-org/"
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}") 