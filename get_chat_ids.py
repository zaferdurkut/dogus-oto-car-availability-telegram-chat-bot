import requests

from config import CAR_CONTROL_TOKEN

url = f"https://api.telegram.org/bot{CAR_CONTROL_TOKEN}/getUpdates"
print(requests.get(url).json())
