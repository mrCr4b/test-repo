import requests

API_KEY = "AIzaSyD4-example-5RaPZb6B3XJ2WqSfhLJs"
endpoint = "https://maps.googleapis.com/maps/api/place/textsearch/json"
params = {
    "query": "restaurants in New York",
    "key": API_KEY
}

response = requests.get(endpoint, params=params)
data = response.json()
print(data)  # In dữ liệu về các nhà hàng ở New York
