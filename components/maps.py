"""
Map Visualization Component for SmartFlow AI.
Generates dark-themed Leaflet/Folium interactive maps with origin/dest markers,
risk-colored route polylines, and hotspot indicators.
"""
from typing import Any, Dict, List, Optional, Tuple
import folium
from folium import plugins


def create_traffic_map(
    start_coords: Optional[Tuple[float, float]] = None,
    dest_coords: Optional[Tuple[float, float]] = None,
    routes: Optional[List[Dict[str, Any]]] = None,
    hotspots: Optional[List[Dict[str, Any]]] = None,
    saved_locations: Optional[List[Dict[str, Any]]] = None,
    center_coords: Tuple[float, float] = (26.9124, 75.7873),  # Default Jaipur center
    zoom_start: int = 12,
    tile_theme: str = "CartoDB dark_matter",
) -> folium.Map:
    """
    Construct a Folium interactive map with dark command-center aesthetic.
    """
    # Auto-adjust center if coordinates are provided
    if start_coords and dest_coords:
        center_lat = (start_coords[0] + dest_coords[0]) / 2.0
        center_lon = (start_coords[1] + dest_coords[1]) / 2.0
        m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start, tiles=tile_theme)
    elif start_coords:
        m = folium.Map(location=list(start_coords), zoom_start=zoom_start, tiles=tile_theme)
    else:
        m = folium.Map(location=list(center_coords), zoom_start=zoom_start, tiles=tile_theme)

    # 1. Render Routes Polylines
    if routes:
        for idx, r in enumerate(reversed(routes)):  # Draw alternatives first, primary on top
            coords = r.get("polyline_coords", [])
            if not coords:
                continue

            is_primary = (r.get("route_index") == 1 or idx == len(routes) - 1)
            level_color = r.get("level_color", "#38BDF8")
            
            # Polyline styling
            weight = 6 if is_primary else 4
            opacity = 0.9 if is_primary else 0.5
            color = level_color if is_primary else "#64748B"
            dash_array = None if is_primary else "6, 6"

            popup_html = f"""
            <div style="font-family: sans-serif; min-width: 150px;">
                <b style="color: #0F172A;">{r.get('label', 'Route')}</b><br/>
                <b>Distance:</b> {r.get('distance_km')} km<br/>
                <b>ETA:</b> {r.get('eta_min')} min<br/>
                <b>Delay:</b> +{r.get('delay_min')} min<br/>
                <b>Risk Score:</b> <span style="color: {level_color}; font-weight: bold;">{r.get('risk_score')}/100</span> ({r.get('traffic_level')})
            </div>
            """

            folium.PolyLine(
                locations=coords,
                color=color,
                weight=weight,
                opacity=opacity,
                dash_array=dash_array,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{r.get('label', 'Route')} - ETA: {r.get('eta_min')}m, Delay: +{r.get('delay_min')}m",
            ).add_to(m)

    # 2. Render Start & Destination Markers
    if start_coords:
        folium.Marker(
            location=list(start_coords),
            popup="<b>Start Origin</b>",
            tooltip="Origin Point",
            icon=folium.Icon(color="green", icon="play", prefix="fa"),
        ).add_to(m)

    if dest_coords:
        folium.Marker(
            location=list(dest_coords),
            popup="<b>Destination</b>",
            tooltip="Destination Point",
            icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa"),
        ).add_to(m)

    # 3. Render Hotspots
    if hotspots:
        for h in hotspots:
            lat = h.get("latitude")
            lon = h.get("longitude")
            if lat is None or lon is None:
                continue

            risk = h.get("current_risk", h.get("average_risk", 50))
            color = "#EF4444" if risk >= 70 else ("#F59E0B" if risk >= 40 else "#10B981")

            folium.CircleMarker(
                location=[lat, lon],
                radius=max(6, min(18, int(risk / 5))),
                color=color,
                weight=2,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                tooltip=f"🔥 Hotspot: {h.get('name')} (Risk: {risk}/100)",
                popup=folium.Popup(f"""
                <div style="font-family: sans-serif;">
                    <b>{h.get('name')}</b><br/>
                    <b>Risk:</b> {risk}/100 ({h.get('traffic_level', 'N/A')})<br/>
                    <b>Delay:</b> +{h.get('delay_min', h.get('average_delay_min', 0))} min<br/>
                    <b>Source:</b> {h.get('data_source', 'Hotspot Engine')}
                </div>
                """, max_width=220),
            ).add_to(m)

    # 4. Render Saved Locations (if given)
    if saved_locations:
        for loc in saved_locations:
            lat = loc.get("latitude")
            lon = loc.get("longitude")
            if lat is None or lon is None:
                continue
            name = loc.get("name", "Saved Point")
            status = loc.get("status", "UNAVAILABLE")
            risk = loc.get("risk_score")

            color = "blue"
            if status == "LIVE" and risk is not None:
                color = "green" if risk < 40 else ("orange" if risk < 70 else "red")

            folium.Marker(
                location=[lat, lon],
                popup=f"<b>{name}</b><br/>{loc.get('address', '')}<br/>Status: {loc.get('display_text', status)}",
                tooltip=f"📍 {name}",
                icon=folium.Icon(color=color, icon="map-marker", prefix="fa"),
            ).add_to(m)

    # Fit bounds if coordinates exist
    if start_coords and dest_coords:
        m.fit_bounds([list(start_coords), list(dest_coords)])

    return m
