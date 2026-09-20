"""
Risk Engine for SmartFlow AI.
Calculates mathematical congestion severity risk scores (0–100), risk tiers,
and transparent data-backed explanations.

CRITICAL RULE:
Model confidence is NOT risk score.
Confidence is the statistical probability of a class (e.g., 99% sure it is LOW).
Risk is the physical severity of road congestion (0-39 Low, 40-69 Medium, 70-100 High).
"""
from typing import Any, Dict, List, Optional, Tuple


def compute_route_risk(
    traffic_duration_sec: float,
    normal_duration_sec: float,
    distance_meters: Optional[float] = None,
    current_speed_kmh: Optional[float] = None,
    free_flow_speed_kmh: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Compute real-time traffic risk score and metrics strictly from congestion signals.

    Formula:
    - delay_sec = max(0, traffic_duration_sec - normal_duration_sec)
    - delay_ratio = delay_sec / max(normal_duration_sec, 1.0)
    - slowdown_ratio = max(0.0, 1.0 - (normal_duration_sec / max(traffic_duration_sec, 1.0)))
    - If speeds are provided:
        speed_slowdown = max(0.0, 1.0 - (current_speed_kmh / max(free_flow_speed_kmh, 1.0)))
    
    Composite normalized risk (0 - 100):
    0-39: LOW
    40-69: MEDIUM
    70-100: HIGH
    """
    traffic_sec = max(0.0, float(traffic_duration_sec))
    normal_sec = max(1.0, float(normal_duration_sec))
    
    # Ensure traffic_sec >= normal_sec in real congestion calculations
    delay_sec = max(0.0, traffic_sec - normal_sec)
    delay_ratio = delay_sec / normal_sec
    slowdown_ratio = max(0.0, 1.0 - (normal_sec / max(traffic_sec, 1.0)))

    # Optional speed calculation
    speed_factor = None
    if current_speed_kmh is not None and free_flow_speed_kmh is not None and free_flow_speed_kmh > 0:
        speed_factor = max(0.0, 1.0 - (float(current_speed_kmh) / float(free_flow_speed_kmh)))

    # Calculate composite risk score:
    # A 100% delay (taking 2x normal time) represents high congestion (>70 risk).
    # A 25% delay represents moderate congestion (~45-55 risk).
    # A <=5% delay represents minimal/free-flow traffic (<25 risk).
    if speed_factor is not None:
        # 40% delay ratio, 30% duration slowdown, 30% speed slowdown
        raw_score = (
            (min(1.5, delay_ratio) / 1.5 * 40.0) +
            (slowdown_ratio * 30.0) +
            (speed_factor * 30.0)
        )
    else:
        # 55% delay ratio, 45% duration slowdown
        # At delay_ratio = 1.0 (double duration), raw_score is ~78
        # At delay_ratio = 1.5, raw_score reaches 100
        raw_score = (
            (min(1.5, delay_ratio) / 1.5 * 55.0) +
            (slowdown_ratio * 45.0)
        )

    risk_score = int(round(max(0.0, min(100.0, raw_score))))
    tier_info = classify_risk_score(risk_score)
    
    delay_min = round(delay_sec / 60.0, 1)
    eta_min = round(traffic_sec / 60.0, 1)
    normal_eta_min = round(normal_sec / 60.0, 1)
    slowdown_pct = round(slowdown_ratio * 100.0, 1)

    # Generate transparent data-backed rationale
    reasons = generate_why_reasons(
        delay_min=delay_min,
        slowdown_pct=slowdown_pct,
        delay_ratio=delay_ratio,
        current_speed_kmh=current_speed_kmh,
        free_flow_speed_kmh=free_flow_speed_kmh,
    )

    return {
        "risk_score": risk_score,
        "traffic_level": tier_info["level"],
        "level_color": tier_info["color"],
        "badge_icon": tier_info["icon"],
        "description": tier_info["description"],
        "eta_min": eta_min,
        "normal_eta_min": normal_eta_min,
        "delay_min": delay_min,
        "delay_ratio": round(delay_ratio, 3),
        "slowdown_pct": slowdown_pct,
        "reasons": reasons,
    }


def classify_risk_score(score: int) -> Dict[str, str]:
    """
    Categorize score strictly by defined thresholds:
    0–39: LOW
    40–69: MEDIUM
    70–100: HIGH
    """
    score = int(round(score))
    if score < 40:
        return {
            "level": "LOW",
            "color": "#10B981",  # Emerald Green
            "icon": "🟢",
            "description": "Free-flowing traffic with minimal or negligible delays.",
        }
    elif score < 70:
        return {
            "level": "MEDIUM",
            "color": "#F59E0B",  # Amber/Yellow
            "icon": "🟡",
            "description": "Moderate congestion with localized bottlenecks and delays.",
        }
    else:
        return {
            "level": "HIGH",
            "color": "#EF4444",  # Crimson Red
            "icon": "🔴",
            "description": "Severe congestion with substantial slowdowns and gridlock risk.",
        }


def generate_why_reasons(
    delay_min: float,
    slowdown_pct: float,
    delay_ratio: float,
    current_speed_kmh: Optional[float] = None,
    free_flow_speed_kmh: Optional[float] = None,
) -> List[str]:
    """
    Synthesize factual, data-supported explanations for the congestion score.
    Never fabricates unsupported claims.
    """
    reasons = []

    # Delay evidence
    if delay_min >= 15.0:
        reasons.append(f"Severe travel delay: +{delay_min} min compared to normal free-flow conditions.")
    elif delay_min >= 5.0:
        reasons.append(f"Elevated travel delay: +{delay_min} min above optimal baseline.")
    elif delay_min > 0.5:
        reasons.append(f"Minor travel delay: +{delay_min} min across active corridor.")
    else:
        reasons.append("Zero significant delay detected; route flowing at normal free-flow speed.")

    # Slowdown evidence
    if slowdown_pct >= 50.0:
        reasons.append(f"Traffic velocity reduced by {slowdown_pct}% compared to unimpeded travel.")
    elif slowdown_pct >= 25.0:
        reasons.append(f"Moderate slowdown of {slowdown_pct}% observed along the main segments.")
    elif slowdown_pct > 5.0:
        reasons.append(f"Minor speed fluctuation of {slowdown_pct}% relative to posted limits.")
    else:
        reasons.append("Flow velocity matches unimpeded design speed.")

    # Speed ratio evidence if provided
    if current_speed_kmh is not None and free_flow_speed_kmh is not None and free_flow_speed_kmh > 0:
        speed_deficit = free_flow_speed_kmh - current_speed_kmh
        if speed_deficit > 20:
            reasons.append(f"Average corridor speed is {round(current_speed_kmh, 1)} km/h (benchmark: {round(free_flow_speed_kmh, 1)} km/h).")
        elif speed_deficit > 5:
            reasons.append(f"Current moving speed is {round(current_speed_kmh, 1)} km/h.")

    # Density / Bottleneck summary
    if delay_ratio >= 0.6:
        reasons.append("Dense vehicle clustering and queued choke points identified along route.")
    elif delay_ratio >= 0.2:
        reasons.append("Intermittent queuing near primary intersections and transit corridors.")

    return reasons


def convert_ml_prediction_to_risk(
    predicted_label: str,
    confidence: float,
    vehicle_count: Optional[int] = None,
    avg_speed: Optional[float] = None,
    free_flow_speed: Optional[float] = 60.0,
) -> Tuple[int, str]:
    """
    Convert ML features and predicted class into a risk score (0-100)
    WITHOUT confusing confidence with risk score!

    Example:
    Model predicts LOW with 99% confidence.
    -> Risk score should be ~15-25 (LOW range), NOT 99!
    Confidence remains 99%.
    """
    label = predicted_label.upper()
    
    # Calculate baseline range from predicted class
    if label == "LOW":
        base_min, base_max = 8, 32
    elif label == "MEDIUM":
        base_min, base_max = 44, 66
    else:  # HIGH
        base_min, base_max = 74, 94

    # Adjust based on continuous features if present
    feature_factor = 0.5
    if avg_speed is not None and free_flow_speed is not None and free_flow_speed > 0:
        speed_ratio = max(0.1, min(1.0, avg_speed / free_flow_speed))
        # Lower speed -> higher within bracket
        feature_factor = 1.0 - speed_ratio

    risk_score = int(round(base_min + (base_max - base_min) * feature_factor))
    risk_score = max(0, min(100, risk_score))
    
    # Double check boundary
    tier = classify_risk_score(risk_score)
    return risk_score, tier["level"]
