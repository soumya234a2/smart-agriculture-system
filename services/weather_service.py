"""
Weather + IoT soil-sensor integration layer.

get_weather() calls the OpenWeatherMap current-weather API when
OPENWEATHER_API_KEY is set in the environment. Without a key (e.g. a
fresh clone with no .env yet), it falls back to a deterministic
synthetic reading so the dashboard and API always work out of the box.

get_sensor_reading() simulates the payload an IoT soil-moisture /
NPK sensor node would push over MQTT/HTTP in the real deployment.
"""
import os
import random
import time
import requests

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(lat=20.4625, lon=85.8830, city="Bhubaneswar"):
    """Returns current temperature, humidity and rainfall probability."""
    if OPENWEATHER_API_KEY:
        try:
            resp = requests.get(
                OPENWEATHER_URL,
                params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"},
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "source": "openweathermap",
                "city": data.get("name", city),
                "temperature_c": data["main"]["temp"],
                "humidity_pct": data["main"]["humidity"],
                "condition": data["weather"][0]["main"],
            }
        except requests.RequestException:
            pass  # fall through to synthetic reading

    random.seed(int(time.time() // 3600))  # changes hourly, stable within the hour
    return {
        "source": "synthetic_fallback",
        "city": city,
        "temperature_c": round(random.uniform(24, 34), 1),
        "humidity_pct": round(random.uniform(55, 85), 1),
        "condition": random.choice(["Clear", "Clouds", "Rain", "Haze"]),
    }


def get_sensor_reading(field_id="field-1"):
    """Simulates a real-time push from a soil-moisture + NPK IoT node."""
    random.seed(f"{field_id}-{int(time.time())}".__hash__() % (2**32))
    return {
        "field_id": field_id,
        "timestamp": time.time(),
        "soil_moisture_pct": round(random.uniform(20, 60), 1),
        "soil_n_kg_ha": round(random.uniform(40, 140), 1),
        "soil_p_kg_ha": round(random.uniform(20, 80), 1),
        "soil_k_kg_ha": round(random.uniform(20, 80), 1),
        "soil_ph": round(random.uniform(5.5, 7.5), 2),
    }
