import requests

data = {
    "heart_rate": 150,
    "spo2": 95,
    "timestamp": "2024-10-02T09:00:06"
}

response = requests.post("http://127.0.0.1:8000/update/", json=data)
print(response.json())
