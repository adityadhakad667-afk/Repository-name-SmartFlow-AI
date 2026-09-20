"""
Routing Service for SmartFlow AI.
Interfaces with Google Routes API (v2) for traffic-aware routing (TRAFFIC_AWARE_OPTIMAL)
and TomTom Routing API as a secondary alternative.

CRITICAL INTEGRITY RULE:
Never fabricates fake live data if API keys are absent. Returns explicit OFFLINE status.
"""
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple
import requests

from analytics.risk_engine import compute_route_risk

logger = logging.getLogger(__name__)


def decode_google_polyline(polyline_str: str) -> List[List[float]]:
    """
    Decode a Google encoded polyline string into [[lat, lon], ...].
    Uses polyline library if installed, with native fallback algorithm.
    """
    if not polyline_str:
        return []
    try:
        import polyline
        coords = polyline.decode(polyline_str)
        return [[float(lat), float(lon)] for lat, lon in coords]
    except Exception:
        pass

    # Native decode algorithm
    index, lat, lng = 0, 0, 0
    coordinates = []
    length = len(polyline_str)

    while index < length:
        # Decode latitude
        shift, result = 0, 0
        while True:
            byte = ord(polyline_str[index]) - 63
            index += 1
            result |= (byte & 0x1F) << shift
            shift += 5
            if byte < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        # Decode longitude
        shift, result = 0, 0
        while True:
            if index >= length:
                break
            byte = ord(polyline_str[index]) - 63
            index += 1
            result |= (byte & 0x1F) << shift
            shift += 5
            if byte < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        coordinates.append([lat / 1e5, lng / 1e5])

    return coordinates


def _parse_duration_string(duration_val: Any) -> float:
    """Parse duration like '1420s' or numeric seconds into float seconds."""
    if isinstance(duration_val, (int, float)):
        return float(duration_val)
    if isinstance(duration_val, str):
        match = re.match(r"^([0-9]+(?:\.[0-9]+)?)s?$", duration_val.strip())
        if match:
            return float(match.group(1))
    return 0.0


def fetch_google_routes(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    api_key: Optional[str] = None,
    routing_preference: str = "TRAFFIC_AWARE_OPTIMAL",
    compute_alternatives: bool = True,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    Query Google Routes API v2 for traffic-aware routes with alternative routes.
    """
    google_key = api_key or os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not google_key:
        return {
            "status": "OFFLINE",
            "provider": "Google Routes API (v2)",
            "error": "Live Traffic is currently unavailable. Configure GOOGLE_MAPS_API_KEY to enable this feature.",
            "routes": [],
        }

    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": google_key,
        "X-Goog-FieldMask": (
            "routes.duration,routes.staticDuration,routes.distanceMeters,"
            "routes.description,routes.polyline.encodedPolyline,routes.travelAdvisory"
        ),
    }

    body = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": float(origin_lat),
                    "longitude": float(origin_lon),
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": float(dest_lat),
                    "longitude": float(dest_lon),
                }
            }
        },
        "travelMode": "DRIVE",
        "routingPreference": routing_preference,
        "computeAlternativeRoutes": compute_alternatives,
        "routeModifiers": {
            "avoidTolls": False,
            "avoidHighways": False,
            "avoidFerries": False,
        },
    }

    try:
        resp = requests.post(url, json=body, headers=headers, timeout=timeout)
        if resp.status_code != 200:
            err_data = {}
            try:
                err_data = resp.json()
            except Exception:
                pass
            err_msg = err_data.get("error", {}).get("message", resp.text)
            logger.error(f"Google Routes API Error: {resp.status_code} - {err_msg}")
            return {
                "status": "ERROR",
                "provider": "Google Routes API (v2)",
                "error": f"Google Routes API responded with error: {err_msg}",
                "routes": [],
            }

        data = resp.json()
        raw_routes = data.get("routes", [])
        if not raw_routes:
            return {
                "status": "NO_ROUTE",
                "provider": "Google Routes API (v2)",
                "error": "No viable driving route found between specified points.",
                "routes": [],
            }

        parsed_routes = []
        for i, r in enumerate(raw_routes):
            duration_sec = _parse_duration_string(r.get("duration", 0))
            # If staticDuration is missing, default to duration
            static_sec = _parse_duration_string(r.get("staticDuration", duration_sec))
            distance_m = float(r.get("distanceMeters", 0))
            description = r.get("description") or f"Route {i + 1}"

            encoded = r.get("polyline", {}).get("encodedPolyline", "")
            coords = decode_google_polyline(encoded)

            # Compute traffic risk metrics
            risk_metrics = compute_route_risk(
                traffic_duration_sec=duration_sec,
                normal_duration_sec=static_sec,
                distance_meters=distance_m,
            )

            parsed_routes.append({
                "route_index": i + 1,
                "label": f"Route {i + 1}" if i > 0 else "Primary Route",
                "description": description,
                "distance_km": round(distance_m / 1000.0, 2),
                "distance_m": distance_m,
                "duration_sec": duration_sec,
                "static_duration_sec": static_sec,
                "eta_min": risk_metrics["eta_min"],
                "normal_eta_min": risk_metrics["normal_eta_min"],
                "delay_min": risk_metrics["delay_min"],
                "slowdown_pct": risk_metrics["slowdown_pct"],
                "risk_score": risk_metrics["risk_score"],
                "traffic_level": risk_metrics["traffic_level"],
                "level_color": risk_metrics["level_color"],
                "badge_icon": risk_metrics["badge_icon"],
                "reasons": risk_metrics["reasons"],
                "polyline_coords": coords,
                "polyline_encoded": encoded,
            })

        return {
            "status": "CONNECTED",
            "provider": "Google Routes API (v2)",
            "error": None,
            "routes": parsed_routes,
        }

    except requests.exceptions.Timeout:
        return {
            "status": "TIMEOUT",
            "provider": "Google Routes API (v2)",
            "error": "Request to Google Routes API timed out. Please check your network.",
            "routes": [],
        }
    except Exception as e:
        logger.exception("Unexpected error querying Google Routes API")
        return {
            "status": "ERROR",
            "provider": "Google Routes API (v2)",
            "error": f"Failed to connect to Google Routes API: {str(e)}",
            "routes": [],
        }


def fetch_tomtom_routes(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    api_key: Optional[str] = None,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    Alternative routing integration via TomTom Routing + Traffic Flow API.
    """
    tomtom_key = api_key or os.environ.get("TOMTOM_API_KEY", "").strip()
    if not tomtom_key:
        return {
            "status": "OFFLINE",
            "provider": "TomTom Routing API",
            "error": "TomTom API key not configured.",
            "routes": [],
        }

    url = (
        f"https://api.tomtom.com/routing/1/calculateRoute/"
        f"{origin_lat},{origin_lon}:{dest_lat},{dest_lon}/json"
    )
    params = {
        "key": tomtom_key,
        "traffic": "true",
        "computeTravelTimeFor": "all",
    }

    try:
        resp = requests.get(url, params=params, timeout=timeout)
        if resp.status_code != 200:
            return {
                "status": "ERROR",
                "provider": "TomTom Routing API",
                "error": f"TomTom API returned status {resp.status_code}",
                "routes": [],
            }
        data = resp.json()
        tt_routes = data.get("routes", [])
        if not tt_routes:
            return {
                "status": "NO_ROUTE",
                "provider": "TomTom Routing API",
                "error": "No TomTom routes found.",
                "routes": [],
            }

        parsed_routes = []
        for i, r in enumerate(tt_routes):
            summary = r.get("summary", {})
            traffic_sec = float(summary.get("travelTimeInSeconds", 0))
            static_sec = float(summary.get("noTrafficTravelTimeInSeconds", traffic_sec))
            distance_m = float(summary.get("lengthInMeters", 0))
            
            # Legs points
            coords = []
            for leg in r.get("legs", []):
                for pt in leg.get("points", []):
                    coords.append([float(pt["latitude"]), float(pt["longitude"])])

            risk_metrics = compute_route_risk(
                traffic_duration_sec=traffic_sec,
                normal_duration_sec=static_sec,
                distance_meters=distance_m,
            )

            parsed_routes.append({
                "route_index": i + 1,
                "label": f"TomTom Route {i + 1}",
                "description": f"Via TomTom traffic-aware route {i + 1}",
                "distance_km": round(distance_m / 1000.0, 2),
                "distance_m": distance_m,
                "duration_sec": traffic_sec,
                "static_duration_sec": static_sec,
                "eta_min": risk_metrics["eta_min"],
                "normal_eta_min": risk_metrics["normal_eta_min"],
                "delay_min": risk_metrics["delay_min"],
                "slowdown_pct": risk_metrics["slowdown_pct"],
                "risk_score": risk_metrics["risk_score"],
                "traffic_level": risk_metrics["traffic_level"],
                "level_color": risk_metrics["level_color"],
                "badge_icon": risk_metrics["badge_icon"],
                "reasons": risk_metrics["reasons"],
                "polyline_coords": coords,
                "polyline_encoded": "",
            })

        return {
            "status": "CONNECTED",
            "provider": "TomTom Routing API",
            "error": None,
            "routes": parsed_routes,
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "provider": "TomTom Routing API",
            "error": str(e),
            "routes": [],
        }


def recommend_route(
    routes: List[Dict[str, Any]],
    preference: str = "Fastest",
) -> Optional[Dict[str, Any]]:
    """
    Select recommended route based on actual data and user preference:
    - 'Fastest': Minimum traffic-aware ETA
    - 'Least Traffic': Minimum traffic delay (delay_min)
    - 'Balanced': Composite scoring balancing ETA and Risk score
    """
    if not routes:
        return None
    if len(routes) == 1:
        return routes[0]

    pref = preference.lower()
    if "least" in pref or "traffic" in pref:
        # Lowest delay
        return min(routes, key=lambda r: (r["delay_min"], r["eta_min"]))
    elif "balanced" in pref:
        # Normalize eta and risk score (50/50 weighting)
        max_eta = max(r["eta_min"] for r in routes) or 1.0
        return min(
            routes,
            key=lambda r: (0.5 * (r["eta_min"] / max_eta) + 0.5 * (r["risk_score"] / 100.0))
        )
    else:
        # Default: Fastest ETA
        return min(routes, key=lambda r: (r["eta_min"], r["risk_score"]))
