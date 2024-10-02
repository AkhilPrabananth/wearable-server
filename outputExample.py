import requests

latest_response = requests.get("http://127.0.0.1:8000/latest/")

# Check if the retrieval was successful
if latest_response.status_code == 200:
    print("\nLatest Prediction:")
    print(latest_response.json())  # Print the latest prediction result
else:
    print("Failed to retrieve latest prediction:")
    print(latest_response.json()) 