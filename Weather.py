import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os

# -----------------------------
# Weather Configuration
# -----------------------------
API_KEY = os.environ["OPENWEATHER_API_KEY"]

LATITUDE = 40.66
LONGITUDE = -73.53

url = (
    "https://api.openweathermap.org/data/2.5/weather"
    f"?lat={LATITUDE}"
    f"&lon={LONGITUDE}"
    f"&units=imperial"
    f"&appid={API_KEY}"
)

forecast_url = (
    "https://api.openweathermap.org/data/2.5/forecast"
    f"?lat={LATITUDE}"
    f"&lon={LONGITUDE}"
    f"&units=imperial"
    f"&appid={API_KEY}"
)

response = requests.get(url)
response.raise_for_status()

data = response.json()

high = round(data["main"]["temp_max"])
low = round(data["main"]["temp_min"])
humidity = data["main"]["humidity"]

sunrise = datetime.fromtimestamp(
    data["sys"]["sunrise"]
).strftime("%I:%M %p")

sunset = datetime.fromtimestamp(
    data["sys"]["sunset"]
).strftime("%I:%M %p")

forecast = requests.get(forecast_url)
forecast.raise_for_status()

forecast_data = forecast.json()

# Next forecast period
next_period = forecast_data["list"][0]

chance_of_rain = int(next_period.get("pop", 0) * 100)

message = f"""Today's Weather

High: {high}°F
Low: {low}°F
Chance of Rain: {chance_of_rain}%
Humidity: {humidity}%
Sunrise: {sunrise}
Sunset: {sunset}
"""

print(message)

# ---------------------------------------
# Send notification with ntfy
# ---------------------------------------

NTFY_TOPIC = os.environ["NTFY_TOPIC"]

headers = {
    "Title": "Today's Weather",
    "Priority": "3",
    "Tags": "partly_sunny"
}

response = requests.post(
    f"https://ntfy.sh/{NTFY_TOPIC}",
    headers=headers,
    data=message.encode("utf-8"),
    timeout=10
)

response.raise_for_status()

print("Notification sent!")