"""
Services module for SmartFlow AI.
Exports Geocoding, Routing, Traffic Orchestration, and Weather integrations.
"""
from .geocoding_service import geocode_address
from .routing_service import (
    fetch_google_routes,
    fetch_tomtom_routes,
    recommend_route,
    decode_google_polyline,
)
from .traffic_service import (
    check_live_traffic_status,
    analyze_live_route,
    monitor_live_locations,
)
from .weather_service import get_weather_context

__all__ = [
    "geocode_address",
    "fetch_google_routes",
    "fetch_tomtom_routes",
    "recommend_route",
    "decode_google_polyline",
    "check_live_traffic_status",
    "analyze_live_route",
    "monitor_live_locations",
    "get_weather_context",
]
