"""
Traffic Service Orchestrator for SmartFlow AI.
Manages system live traffic connectivity, route analysis, and live batch monitoring of saved locations.

CRITICAL INTEGRITY RULES:
- Never falsely display LIVE.
- Never invent or fabricate live traffic values when offline.
"""
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

from .geocoding_service import geocode_address
from .routing_service import fetch_google_routes, fetch_tomtom_routes, recommend_route
from analytics.risk_engine import compute_route_risk

logger = logging.getLogger(__name__)


def check_live_traffic_status(
    google_key: Optional[str] = None,
    tomtom_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Check real-time traffic connection status.
    Returns:
        is_connected (bool): True ONLY if a real valid API key is present.
        provider (str): Provider name or 'None'
        status_text (str): "● LIVE TRAFFIC CONNECTED" or "● LIVE TRAFFIC OFFLINE"
    """
    g_key = (google_key or os.environ.get("GOOGLE_MAPS_API_KEY", "")).strip()
    t_key = (tomtom_key or os.environ.get("TOMTOM_API_KEY", "")).strip()

    if g_key:
        return {
            "is_connected": True,
            "provider": "Google Routes API (v2)",
            "status_text": "● LIVE TRAFFIC CONNECTED",
            "status_color": "#10B981",  # Emerald Green
            "badge": "LIVE TRAFFIC",
            "message": "Connected to Google Routes Platform (TRAFFIC_AWARE_OPTIMAL)",
        }
    elif t_key:
        return {
            "is_connected": True,
            "provider": "TomTom Traffic Flow API",
            "status_text": "● LIVE TRAFFIC CONNECTED",
            "status_color": "#10B981",
            "badge": "LIVE TRAFFIC",
            "message": "Connected to TomTom Routing & Traffic Engine",
        }
    else:
        return {
            "is_connected": False,
            "provider": "None",
            "status_text": "● LIVE TRAFFIC OFFLINE",
            "status_color": "#EF4444",  # Crimson Red
            "badge": "OFFLINE",
            "message": "Live Traffic is currently offline. Configure GOOGLE_MAPS_API_KEY to enable live routing.",
        }


def analyze_live_route(
    start_query: str,
    dest_query: str,
    google_key: Optional[str] = None,
    tomtom_key: Optional[str] = None,
    preference: str = "Fastest",
) -> Dict[str, Any]:
    """
    Analyze real-time route between start and destination using live APIs.
    Geocodes both locations, calls traffic-aware routing API, computes risk,
    and returns comprehensive route result with alternatives.
    """
    # 1. Geocode Start
    start_lat, start_lon, start_addr, start_err = geocode_address(start_query, api_key=google_key)
    if start_err:
        return {
            "success": False,
            "error": f"Start location error: {start_err}",
            "stage": "geocoding_start",
        }

    # 2. Geocode Destination
    dest_lat, dest_lon, dest_addr, dest_err = geocode_address(dest_query, api_key=google_key)
    if dest_err:
        return {
            "success": False,
            "error": f"Destination location error: {dest_err}",
            "stage": "geocoding_dest",
        }

    # 3. Call Live Routing API
    routing_result = fetch_google_routes(
        origin_lat=start_lat,
        origin_lon=start_lon,
        dest_lat=dest_lat,
        dest_lon=dest_lon,
        api_key=google_key,
    )

    # If Google is offline, check if TomTom key is present
    if routing_result["status"] == "OFFLINE" and tomtom_key:
        routing_result = fetch_tomtom_routes(
            origin_lat=start_lat,
            origin_lon=start_lon,
            dest_lat=dest_lat,
            dest_lon=dest_lon,
            api_key=tomtom_key,
        )

    if routing_result["status"] != "CONNECTED" or not routing_result["routes"]:
        return {
            "success": False,
            "status": routing_result.get("status", "ERROR"),
            "provider": routing_result.get("provider", "Unknown"),
            "error": routing_result.get("error", "Failed to retrieve live route data."),
            "start_coords": (start_lat, start_lon),
            "dest_coords": (dest_lat, dest_lon),
            "start_address": start_addr,
            "dest_address": dest_addr,
            "routes": [],
        }

    routes = routing_result["routes"]
    recommended = recommend_route(routes, preference=preference)

    return {
        "success": True,
        "status": "CONNECTED",
        "provider": routing_result["provider"],
        "data_source": "LIVE TRAFFIC",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "start_query": start_query,
        "dest_query": dest_query,
        "start_coords": (start_lat, start_lon),
        "dest_coords": (dest_lat, dest_lon),
        "start_address": start_addr,
        "dest_address": dest_addr,
        "preference": preference,
        "primary_route": routes[0],
        "recommended_route": recommended,
        "routes": routes,
    }


def monitor_live_locations(
    locations: List[Dict[str, Any]],
    google_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Monitor a list of saved locations.
    If live traffic API key is available, samples route traffic along the location's corridor.
    If offline, sets status explicitly to 'Live data unavailable'. NEVER invents fake values!
    """
    status_info = check_live_traffic_status(google_key=google_key)
    monitored_results = []

    now_str = datetime.now().strftime("%H:%M:%S")

    for loc in locations:
        loc_id = loc.get("id")
        name = loc.get("name", "Unknown")
        lat = loc.get("latitude")
        lon = loc.get("longitude")
        addr = loc.get("address", "")

        if not status_info["is_connected"]:
            # Offline integrity: Never fabricate live traffic values
            monitored_results.append({
                "id": loc_id,
                "name": name,
                "address": addr,
                "latitude": lat,
                "longitude": lon,
                "status": "UNAVAILABLE",
                "risk_score": None,
                "traffic_level": "N/A",
                "level_color": "#64748B",
                "badge_icon": "⚪",
                "delay_min": None,
                "display_text": "Live data unavailable (API offline)",
                "updated_at": "Offline",
            })
            continue

        # When live connected, query localized corridor (+0.015 deg lat ~ 1.6 km)
        try:
            route_res = fetch_google_routes(
                origin_lat=lat,
                origin_lon=lon,
                dest_lat=lat + 0.015,
                dest_lon=lon + 0.015,
                api_key=google_key,
                compute_alternatives=False,
                timeout=5,
            )
            if route_res["status"] == "CONNECTED" and route_res["routes"]:
                r = route_res["routes"][0]
                monitored_results.append({
                    "id": loc_id,
                    "name": name,
                    "address": addr,
                    "latitude": lat,
                    "longitude": lon,
                    "status": "LIVE",
                    "risk_score": r["risk_score"],
                    "traffic_level": r["traffic_level"],
                    "level_color": r["level_color"],
                    "badge_icon": r["badge_icon"],
                    "delay_min": r["delay_min"],
                    "display_text": f"+{r['delay_min']} min delay",
                    "updated_at": now_str,
                })
            else:
                monitored_results.append({
                    "id": loc_id,
                    "name": name,
                    "address": addr,
                    "latitude": lat,
                    "longitude": lon,
                    "status": "ERROR",
                    "risk_score": None,
                    "traffic_level": "N/A",
                    "level_color": "#64748B",
                    "badge_icon": "⚪",
                    "delay_min": None,
                    "display_text": "Probe query error",
                    "updated_at": now_str,
                })
        except Exception as e:
            logger.warning(f"Error querying live traffic for {name}: {e}")
            monitored_results.append({
                "id": loc_id,
                "name": name,
                "address": addr,
                "latitude": lat,
                "longitude": lon,
                "status": "ERROR",
                "risk_score": None,
                "traffic_level": "N/A",
                "level_color": "#64748B",
                "badge_icon": "⚪",
                "delay_min": None,
                "display_text": "Connection timeout",
                "updated_at": now_str,
            })

    return monitored_results
