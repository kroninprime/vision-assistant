"""
Example skill that can be triggered when the word "weather" appears in the prompt.
Extend this pattern to add more capabilities.
"""

from app.main import assistant


def weather_skill(prompt: str) -> str:
    # TODO: integrate a real weather API
    return "Weather skill placeholder: connect me to a real API to give forecasts."


assistant.register("weather", ["weather", "forecast", "temperature"], weather_skill)
