"""
Traffic Forecasting Engine for SmartFlow AI.
Projects congestion trends, risk scores, and confidence trajectories for the next 3h and 6h windows.

CRITICAL INVARIANT:
Outputs are explicitly labeled 'MODEL FORECAST' and never confused with real-time live data.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List
import numpy as np


def generate_traffic_forecast(
    horizon_hours: int = 6,
    base_road_type: str = "Arterial",
    base_weather: str = "Clear",
    base_temperature: float = 28.0,
    base_vehicle_count: int = 700,
    free_flow_speed: float = 60.0,
    start_time: datetime = None,
) -> Dict[str, Any]:
    """
    Generate multi-hour forward projection based on time-shifted feature modeling.
    Simulates diurnal traffic volume fluctuations, solar thermal transitions, and capacity thresholds.
    """
    from ml.predict import predict_traffic_conditions

    if start_time is None:
        start_time = datetime.now()

    forecast_points = []
    horizon_hours = min(12, max(1, horizon_hours))

    for step in range(1, horizon_hours + 1):
        target_time = start_time + timedelta(hours=step)
        hour = target_time.hour
        day_of_week = target_time.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0

        # Estimate vehicle volume progression based on diurnal curve
        if not is_weekend:
            if 8 <= hour <= 10:
                mult = 1.35  # Morning peak
            elif 17 <= hour <= 20:
                mult = 1.40  # Evening peak
            elif 11 <= hour <= 16:
                mult = 0.85  # Normal midday
            elif 21 <= hour <= 23:
                mult = 0.50  # Late evening
            else:
                mult = 0.25  # Night/dawn
        else:
            if 13 <= hour <= 19:
                mult = 1.05  # Weekend afternoon
            else:
                mult = 0.40

        v_count = int(base_vehicle_count * mult)
        # Moderate temperature variations
        temp = base_temperature - (1.5 if (hour >= 20 or hour <= 6) else -0.8)

        pred = predict_traffic_conditions(
            hour=hour,
            day_of_week=day_of_week,
            road_type=base_road_type,
            weather=base_weather,
            temperature=round(temp, 1),
            precipitation=0.0 if base_weather == "Clear" else 2.5,
            vehicle_count=v_count,
            free_flow_speed=free_flow_speed,
        )

        forecast_points.append({
            "step": step,
            "forecast_time": target_time.strftime("%H:%M"),
            "hour": hour,
            "full_timestamp": target_time.strftime("%Y-%m-%d %H:%M"),
            "predicted_traffic": pred["predicted_class"],
            "risk_score": pred["risk_score"],
            "confidence_pct": pred["confidence_pct"],
            "level_color": pred["level_color"],
            "badge_icon": pred["badge_icon"],
            "estimated_vehicles": v_count,
            "temperature": round(temp, 1),
            "ai_insight": pred["ai_insight"],
        })

    return {
        "label": "MODEL FORECAST",
        "horizon_hours": horizon_hours,
        "generated_at": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "points": forecast_points,
    }
