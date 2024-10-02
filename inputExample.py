import requests

data = {
    "heart_rate": 20,
    "spo2": 91,
    "timestamp": "2024-10-02T09:00:06"
}

response = requests.post("https://wearable-server.onrender.com/update/", json=data)
print(response.json())
