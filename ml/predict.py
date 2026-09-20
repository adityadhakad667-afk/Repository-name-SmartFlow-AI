"""
Prediction interface for SmartFlow AI ML subsystem.
Handles real-time feature inference, confidence extraction, and risk conversion.

CRITICAL INVARIANT:
Data source is explicitly labeled 'ML PREDICTION'.
Confidence is separate from Risk Score.
"""
from typing import Any, Dict, Optional
from datetime import datetime

from .model import TrafficModel
from analytics.risk_engine import convert_ml_prediction_to_risk, classify_risk_score

_MODEL_INSTANCE: Optional[TrafficModel] = None


def get_model_instance() -> TrafficModel:
    """Singleton getter for the trained model."""
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        _MODEL_INSTANCE = TrafficModel()
    return _MODEL_INSTANCE


def predict_traffic_conditions(
    hour: int,
    day_of_week: int,
    road_type: str = "Arterial",
    weather: str = "Clear",
    temperature: float = 28.0,
    precipitation: float = 0.0,
    vehicle_count: int = 650,
    free_flow_speed: float = 60.0,
) -> Dict[str, Any]:
    """
    Predict traffic congestion using the trained machine learning model.
    """
    model = get_model_instance()
    if not model.is_loaded():
        # Attempt to trigger on-demand training
        from .train import train_models
        train_models()
        model.load()

    is_weekend = 1 if day_of_week >= 5 else 0

    features = {
        "hour": int(hour),
        "day_of_week": int(day_of_week),
        "is_weekend": is_weekend,
        "road_type": str(road_type),
        "weather": str(weather),
        "temperature": float(temperature),
        "precipitation": float(precipitation),
        "vehicle_count": int(vehicle_count),
        "free_flow_speed": float(free_flow_speed),
    }

    raw_result = model.predict_one(features)
    predicted_class = raw_result["predicted_class"]
    confidence = raw_result["confidence"]

    # Invariant: Model confidence is NOT risk.
    # Risk represents congestion severity, confidence represents model certainty.
    risk_score, risk_level = convert_ml_prediction_to_risk(
        predicted_label=predicted_class,
        confidence=confidence,
        vehicle_count=vehicle_count,
        avg_speed=None,
        free_flow_speed=free_flow_speed,
    )
    tier_info = classify_risk_score(risk_score)

    # Synthesize AI insight narrative
    ai_insight = generate_ai_insight(
        predicted_class=predicted_class,
        hour=hour,
        road_type=road_type,
        weather=weather,
        vehicle_count=vehicle_count,
        confidence=confidence,
    )

    return {
        "data_source": "ML PREDICTION",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "predicted_class": predicted_class,
        "confidence_pct": round(confidence * 100.0, 1),
        "risk_score": risk_score,
        "traffic_level": tier_info["level"],
        "level_color": tier_info["color"],
        "badge_icon": tier_info["icon"],
        "description": tier_info["description"],
        "probabilities": raw_result["probabilities"],
        "feature_contributions": raw_result["feature_contributions"],
        "ai_insight": ai_insight,
        "model_name": raw_result["model_name"],
        "input_features": features,
    }


def generate_ai_insight(
    predicted_class: str,
    hour: int,
    road_type: str,
    weather: str,
    vehicle_count: int,
    confidence: float,
) -> str:
    """Generate dynamic transparent narrative describing the primary driver behind the ML prediction."""
    is_peak = (8 <= hour <= 10) or (17 <= hour <= 20)

    if predicted_class == "HIGH":
        if is_peak and vehicle_count > 900:
            return (
                f"Elevated vehicle concentration ({vehicle_count} veh/hr) coinciding with standard rush-hour "
                f"demand ({hour:02d}:00) is the dominant factor driving the HIGH congestion forecast."
            )
        elif weather in ["Storm", "Rain"]:
            return (
                f"Adverse weather conditions ({weather}) coupled with dense corridor traffic significantly degrade "
                f"braking distances and throughput capacity on this {road_type} segment."
            )
        else:
            return (
                f"Vehicle volume exceeds {road_type} design threshold, leading to anticipated queue formation "
                f"and elevated travel risk."
            )
    elif predicted_class == "MEDIUM":
        return (
            f"Moderate vehicular flow ({vehicle_count} veh/hr) with stable throughput. Minor localized queueing "
            f"expected around key convergence intersections."
        )
    else:  # LOW
        return (
            f"Off-peak operational window ({hour:02d}:00) with volume well within infrastructure capacity. "
            f"Vehicles are projected to traverse near free-flow design velocity."
        )
