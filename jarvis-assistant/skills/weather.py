import requests
from app.main import assistant

# Default coordinates (e.g., Chennai, India); adjust as needed.
DEFAULT_LAT = 13.0827
DEFAULT_LON = 80.2707


def weather_skill(prompt: str) -> str:
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": DEFAULT_LAT,
                "longitude": DEFAULT_LON,
                "current_weather": True,
                "hourly": "temperature_2m",
            },
            timeout=5,
        )
        data = resp.json()
        cw = data.get("current_weather", {})
        temp = cw.get("temperature")
        wind = cw.get("windspeed")
        if temp is None:
            return "Weather service unavailable."
        return f"It is {temp}°C with wind {wind} km/h at your default location."
    except Exception:
        return "Weather service unavailable."


assistant.register("weather live", ["weather", "temperature", "forecast", "climate"], weather_skill)
