"""
Analytics module for SmartFlow AI.
Includes risk calculation, forecasting, and traffic hotspot detection.
"""
from .risk_engine import (
    compute_route_risk,
    classify_risk_score,
    generate_why_reasons,
    convert_ml_prediction_to_risk,
)
from .forecasting import generate_traffic_forecast
from .hotspot_engine import get_historical_hotspots, get_live_hotspots

__all__ = [
    "compute_route_risk",
    "classify_risk_score",
    "generate_why_reasons",
    "convert_ml_prediction_to_risk",
    "generate_traffic_forecast",
    "get_historical_hotspots",
    "get_live_hotspots",
]
