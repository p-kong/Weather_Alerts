from zoneinfo import ZoneInfo

import requests
import smtplib
from email.message import EmailMessage
import os
from datetime import datetime, timezone, timedelta

# -----------------------------
# Weather Configuration
# -----------------------------
API_KEY = os.environ["OPENWEATHER_API_KEY"]

LATITUDE = 40.672
LONGITUDE = -73.535

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


humidity = data["main"]["humidity"]


tz = ZoneInfo("America/New_York")
today = datetime.now(tz).date()

sunrise = datetime.fromtimestamp(
    data["sys"]["sunrise"],
    tz=tz
).strftime("%I:%M %p")

sunset = datetime.fromtimestamp(
    data["sys"]["sunset"],
    tz=tz
).strftime("%I:%M %p")

forecast = requests.get(forecast_url)
forecast.raise_for_status()

forecast_data = forecast.json()
forecast_list = forecast_data["list"]

temps = [
    item["main"]["temp"]
    for item in forecast_list
    if datetime.fromtimestamp(item["dt"], tz).date() == today
]

high = round(max(temps)) if temps else round(data["main"]["temp"])
low = round(min(temps)) if temps else round(data["main"]["temp"])

rain_chances = [
    item.get("pop", 0)
    for item in forecast_list
    if datetime.fromtimestamp(item["dt"], tz).date() == today
]

chance_of_rain = round(max(rain_chances, default=0) * 100)


feels_like = round(data["main"]["feels_like"])
current_temp = round(data["main"]["temp"])

# Next forecast period
next_period = forecast_data["list"][0]

chance_of_rain = int(next_period.get("pop", 0) * 100)

message = f"""Today's Weather

Current Temp: {current_temp}°F
Feels Like: {feels_like}°F
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

