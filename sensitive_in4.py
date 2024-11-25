import requests

def fetch_data_from_api(endpoint):
    # Khóa API được phích cứng vào trong hàm (không an toàn)
    API_KEY = "AIzaSyD4-example-5RaPZb6B3XJ2WqSfhLJs"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    # Giả lập yêu cầu API (ví dụ)
    response = requests.get(endpoint, headers=headers)
    return response.json()

# Gọi hàm với endpoint mẫu
data = fetch_data_from_api("https://api.example.com/data")
print(data)
