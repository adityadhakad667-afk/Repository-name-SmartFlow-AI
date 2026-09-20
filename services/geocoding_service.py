"""
Geocoding Service for SmartFlow AI.
Resolves global text addresses and landmark queries to coordinates (lat, lon, formatted_address).
Supports Google Geocoding API with Nominatim (OSM) fallback.
"""
import logging
import os
import urllib.parse
from typing import Any, Dict, Optional, Tuple
import requests

logger = logging.getLogger(__name__)

# In-memory session cache to avoid repeated geocoding requests
_GEOCODE_CACHE: Dict[str, Tuple[float, float, str]] = {
    # Pre-seeded common reference queries for instant fallback
    "jaipur railway station": (26.9196, 75.7878, "Jaipur Junction Railway Station, Gopalbari, Jaipur, Rajasthan, India"),
    "hawa mahal": (26.9239, 75.8267, "Hawa Mahal, Badi Choupad, J.D.A. Market, Jaipur, Rajasthan, India"),
    "mi road": (26.9167, 75.8055, "Mirza Ismail Road, Jaipur, Rajasthan, India"),
    "c-scheme": (26.9073, 75.8016, "C-Scheme, Ashok Nagar, Jaipur, Rajasthan, India"),
    "world trade park": (26.8532, 75.8050, "World Trade Park, Malviya Nagar, Jaipur, Rajasthan, India"),
    "civil lines": (26.9080, 75.7794, "Civil Lines, Jaipur, Rajasthan, India"),
    "delhi": (28.6139, 77.2090, "New Delhi, Delhi, India"),
    "mumbai": (19.0760, 72.8777, "Mumbai, Maharashtra, India"),
    "bangalore": (12.9716, 77.5946, "Bengaluru, Karnataka, India"),
    "gurgaon": (28.4595, 77.0266, "Gurugram, Haryana, India"),
    "new york": (40.7128, -74.0060, "New York, NY, USA"),
    "london": (51.5074, -0.1278, "London, Greater London, England, UK"),
}


def geocode_address(
    query: str,
    api_key: Optional[str] = None,
    timeout: int = 6,
) -> Tuple[Optional[float], Optional[float], Optional[str], Optional[str]]:
    """
    Resolve address to (latitude, longitude, formatted_address, error_msg).
    
    Tries in sequence:
    1. Memory cache
    2. Google Geocoding API (if api_key provided or found in environment)
    3. OpenStreetMap Nominatim public geocoding API (graceful open fallback)
    """
    query_clean = query.strip()
    if not query_clean:
        return None, None, None, "Location query cannot be empty."

    cache_key = query_clean.lower()
    if cache_key in _GEOCODE_CACHE:
        lat, lon, addr = _GEOCODE_CACHE[cache_key]
        return lat, lon, addr, None

    google_key = api_key or os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()

    # 1. Try Google Geocoding if key configured
    if google_key:
        try:
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(query_clean)}&key={google_key}"
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "OK" and data.get("results"):
                    first = data["results"][0]
                    loc = first["geometry"]["location"]
                    lat, lon = float(loc["lat"]), float(loc["lng"])
                    formatted = first.get("formatted_address", query_clean)
                    _GEOCODE_CACHE[cache_key] = (lat, lon, formatted)
                    return lat, lon, formatted, None
                elif data.get("status") == "ZERO_RESULTS":
                    return None, None, None, f"Address '{query_clean}' not found on Google Maps."
                else:
                    logger.warning(f"Google Geocoding status: {data.get('status')}: {data.get('error_message')}")
        except Exception as e:
            logger.warning(f"Google Geocoding error: {e}")

    # 2. Try OpenStreetMap Nominatim geocoding fallback
    try:
        headers = {"User-Agent": "SmartFlow-AI-Traffic-Intelligence/1.0 (contact: support@smartflow.ai)"}
        nom_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query_clean)}&format=json&limit=1"
        resp = requests.get(nom_url, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            results = resp.json()
            if results and len(results) > 0:
                lat = float(results[0]["lat"])
                lon = float(results[0]["lon"])
                display_name = results[0].get("display_name", query_clean)
                _GEOCODE_CACHE[cache_key] = (lat, lon, display_name)
                return lat, lon, display_name, None
    except Exception as e:
        logger.warning(f"Nominatim geocoding error: {e}")

    return None, None, None, f"Could not resolve coordinates for '{query_clean}'. Please verify spelling or internet connection."
