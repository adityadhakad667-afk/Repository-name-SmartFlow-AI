"""
Hotspot Detection Engine for SmartFlow AI.
Identifies and ranks geographic and network bottlenecks using actual live monitor data
or historical observation datasets.

CRITICAL INVARIANT:
Live hotspots and Historical hotspots are strictly segregated and labeled.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np

from ml.preprocessing import SAMPLE_DATA_PATH, load_or_generate_dataset
from database.db import get_saved_locations, get_route_history


def get_historical_hotspots(data_path: Path = SAMPLE_DATA_PATH, top_n: int = 8) -> List[Dict[str, Any]]:
    """
    Extract high-congestion hotspot corridors from the historical traffic dataset.
    Ranks by historical risk score, average delay, and congestion frequency.
    """
    df = load_or_generate_dataset(data_path)

    # Reference corridor definitions mapped to dataset combinations
    corridor_definitions = [
        {"name": "MI Road Commercial Artery", "lat": 26.9167, "lon": 75.8055, "road_type": "Arterial"},
        {"name": "Ajmer Road Express Flyover", "lat": 26.8920, "lon": 75.7600, "road_type": "Highway"},
        {"name": "Tonk Road Transit Chokepoint", "lat": 26.8650, "lon": 75.8020, "road_type": "Arterial"},
        {"name": "JLN Marg Education & Hospital Zone", "lat": 26.8780, "lon": 75.8110, "road_type": "Arterial"},
        {"name": "Badi Choupad Old City Gateway", "lat": 26.9240, "lon": 75.8270, "road_type": "Urban"},
        {"name": "Transport Nagar Bypass Interchange", "lat": 26.9050, "lon": 75.8500, "road_type": "Highway"},
        {"name": "Sanganer Airport Link Road", "lat": 26.8300, "lon": 75.8050, "road_type": "Arterial"},
        {"name": "Sodala Elevated Corridor Junction", "lat": 26.9020, "lon": 75.7720, "road_type": "Arterial"},
    ]

    hotspots = []
    for i, corr in enumerate(corridor_definitions[:top_n]):
        rtype = corr["road_type"]
        sub = df[df["road_type"] == rtype]
        if len(sub) == 0:
            sub = df

        avg_risk = int(round(sub["risk_score"].mean()))
        avg_delay = round(float(sub["delay_min"].mean()), 1)
        high_freq = round(float((sub["congestion_level"] == "HIGH").mean() * 100), 1)

        # Risk level classification
        if avg_risk >= 70:
            level = "HIGH"
            color = "#EF4444"
            icon = "🔴"
        elif avg_risk >= 40:
            level = "MEDIUM"
            color = "#F59E0B"
            icon = "🟡"
        else:
            level = "LOW"
            color = "#10B981"
            icon = "🟢"

        hotspots.append({
            "rank": i + 1,
            "name": corr["name"],
            "latitude": corr["lat"],
            "longitude": corr["lon"],
            "road_type": rtype,
            "data_source": "HISTORICAL DATA",
            "average_risk": avg_risk,
            "average_delay_min": avg_delay,
            "high_risk_frequency_pct": high_freq,
            "traffic_level": level,
            "level_color": color,
            "badge_icon": icon,
            "sample_size": len(sub),
        })

    # Sort by average risk descending
    hotspots.sort(key=lambda x: x["average_risk"], reverse=True)
    for i, h in enumerate(hotspots):
        h["rank"] = i + 1

    return hotspots


def get_live_hotspots(monitored_locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank current hotspots from live monitored locations.
    Only includes locations with verified live data.
    """
    valid_live = [m for m in monitored_locations if m.get("status") == "LIVE" and m.get("risk_score") is not None]
    if not valid_live:
        return []

    sorted_live = sorted(valid_live, key=lambda x: x["risk_score"], reverse=True)
    hotspots = []
    for i, item in enumerate(sorted_live):
        hotspots.append({
            "rank": i + 1,
            "name": item["name"],
            "address": item["address"],
            "latitude": item["latitude"],
            "longitude": item["longitude"],
            "data_source": "LIVE TRAFFIC",
            "current_risk": item["risk_score"],
            "delay_min": item["delay_min"],
            "traffic_level": item["traffic_level"],
            "level_color": item["level_color"],
            "badge_icon": item["badge_icon"],
            "updated_at": item["updated_at"],
        })
    return hotspots
