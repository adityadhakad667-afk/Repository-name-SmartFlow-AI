"""
Weather Service for SmartFlow AI.
Provides ambient meteorological context (temperature, precipitation, weather conditions)
influencing traffic flow and ML model features.
Integrates free Open-Meteo API with offline fallback.
"""
import logging
from typing import Any, Dict
import requests

logger = logging.getLogger(__name__)

# WMO Weather interpretation codes mapping
WMO_CODE_MAP = {
    0: ("Clear", 0.0),
    1: ("Mainly Clear", 0.0),
    2: ("Partly Cloudy", 0.0),
    3: ("Overcast", 0.0),
    45: ("Fog", 0.0),
    48: ("Depositing Rime Fog", 0.0),
    51: ("Light Drizzle", 0.5),
    53: ("Moderate Drizzle", 1.0),
    55: ("Dense Drizzle", 2.0),
    61: ("Slight Rain", 1.5),
    63: ("Moderate Rain", 4.0),
    65: ("Heavy Rain", 8.0),
    71: ("Slight Snow", 1.0),
    80: ("Rain Showers", 3.0),
    95: ("Thunderstorm", 10.0),
}


def get_weather_context(lat: float, lon: float, timeout: int = 4) -> Dict[str, Any]:
    """
    Fetch current ambient weather for coordinates.
    Uses free Open-Meteo forecast API (no API key required).
    """
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code"
        )
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            curr = data.get("current", {})
            wmo_code = curr.get("weather_code", 0)
            condition, default_precip = WMO_CODE_MAP.get(wmo_code, ("Clear", 0.0))
            precip = float(curr.get("precipitation", default_precip))
            temp = float(curr.get("temperature_2m", 25.0))
            humidity = float(curr.get("relative_humidity_2m", 50.0))

            # Group condition into ML categories: Clear, Rain, Fog, Storm
            ml_condition = "Clear"
            if "Rain" in condition or "Drizzle" in condition:
                ml_condition = "Rain"
            elif "Fog" in condition:
                ml_condition = "Fog"
            elif "Thunderstorm" in condition or precip > 5.0:
                ml_condition = "Storm"

            return {
                "condition": condition,
                "ml_condition": ml_condition,
                "temperature_c": temp,
                "precipitation_mm": precip,
                "humidity_pct": humidity,
                "is_live": True,
            }
    except Exception as e:
        logger.warning(f"Could not fetch live weather from Open-Meteo: {e}")

    # Fallback default pleasant conditions
    return {
        "condition": "Clear",
        "ml_condition": "Clear",
        "temperature_c": 28.0,
        "precipitation_mm": 0.0,
        "humidity_pct": 45.0,
        "is_live": False,
    }
