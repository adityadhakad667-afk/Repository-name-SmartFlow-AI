"""
Demo Mode Component for SmartFlow AI.
Enables offline presentations, investor pitches, and testing without requiring live API keys.

CRITICAL INVARIANTS:
- Prominently displays 'SIMULATED DEMO DATA'.
- Never labels simulated data as real-time.
- 100% operational offline.
"""
from typing import Any, Dict
import streamlit as st
from streamlit_folium import st_folium

from analytics.risk_engine import compute_route_risk
from database.db import log_route_history
from .risk_cards import render_risk_gauge_panel, render_why_box
from .maps import create_traffic_map


# Pre-configured simulated presentation scenarios
DEMO_SCENARIOS = {
    "Peak Hour Rush (Morning Commute)": {
        "title": "Jaipur Railway Station ➔ Hawa Mahal (Morning Peak)",
        "start": "Jaipur Railway Station",
        "dest": "Hawa Mahal",
        "start_coords": (26.9196, 75.7878),
        "dest_coords": (26.9239, 75.8267),
        "distance_km": 5.4,
        "distance_m": 5400,
        "normal_duration_sec": 840,   # 14 min
        "traffic_duration_sec": 1560, # 26 min (+12 min delay)
        "routes": [
            {
                "route_index": 1,
                "label": "Primary Route (via MI Road)",
                "description": "Via Mirza Ismail Road & Badi Choupad",
                "distance_km": 5.4,
                "distance_m": 5400,
                "normal_duration_sec": 840,
                "traffic_duration_sec": 1560,
                "polyline_coords": [
                    [26.9196, 75.7878], [26.9180, 75.7950], [26.9167, 75.8055],
                    [26.9190, 75.8150], [26.9220, 75.8220], [26.9239, 75.8267]
                ],
            },
            {
                "route_index": 2,
                "label": "Alternative Route (via Station Rd)",
                "description": "Via Station Road & Chandpole Gate",
                "distance_km": 5.8,
                "distance_m": 5800,
                "normal_duration_sec": 900,
                "traffic_duration_sec": 1380, # 23 min
                "polyline_coords": [
                    [26.9196, 75.7878], [26.9230, 75.7950], [26.9250, 75.8050],
                    [26.9245, 75.8180], [26.9239, 75.8267]
                ],
            }
        ]
    },
    "Normal Traffic (Off-Peak Free Flow)": {
        "title": "World Trade Park ➔ Civil Lines (Off-Peak)",
        "start": "World Trade Park",
        "dest": "Civil Lines",
        "start_coords": (26.8532, 75.8050),
        "dest_coords": (26.9080, 75.7794),
        "distance_km": 8.6,
        "distance_m": 8600,
        "normal_duration_sec": 960,   # 16 min
        "traffic_duration_sec": 1020, # 17 min (+1 min delay)
        "routes": [
            {
                "route_index": 1,
                "label": "Primary Route (via JLN Marg)",
                "description": "Direct flow via JLN Marg express corridor",
                "distance_km": 8.6,
                "distance_m": 8600,
                "normal_duration_sec": 960,
                "traffic_duration_sec": 1020,
                "polyline_coords": [
                    [26.8532, 75.8050], [26.8700, 75.8080], [26.8850, 75.8040],
                    [26.8980, 75.7900], [26.9080, 75.7794]
                ],
            }
        ]
    },
    "Heavy Gridlock & Incident (Storm Scenario)": {
        "title": "C-Scheme ➔ Transport Nagar (Severe Bottleneck)",
        "start": "C-Scheme",
        "dest": "Transport Nagar Bypass",
        "start_coords": (26.9073, 75.8016),
        "dest_coords": (26.9050, 75.8500),
        "distance_km": 6.8,
        "distance_m": 6800,
        "normal_duration_sec": 900,   # 15 min
        "traffic_duration_sec": 2400, # 40 min (+25 min delay)
        "routes": [
            {
                "route_index": 1,
                "label": "Primary Corridor (Gridlock)",
                "description": "Via Tonk Road & Ghat Gate tunnel",
                "distance_km": 6.8,
                "distance_m": 6800,
                "normal_duration_sec": 900,
                "traffic_duration_sec": 2400,
                "polyline_coords": [
                    [26.9073, 75.8016], [26.9020, 75.8150], [26.9000, 75.8300],
                    [26.9030, 75.8420], [26.9050, 75.8500]
                ],
            }
        ]
    },
    "Moderate Midday Transit": {
        "title": "Civil Lines ➔ MI Road Commercial Belt",
        "start": "Civil Lines",
        "dest": "MI Road",
        "start_coords": (26.9080, 75.7794),
        "dest_coords": (26.9167, 75.8055),
        "distance_km": 3.6,
        "distance_m": 3600,
        "normal_duration_sec": 480,  # 8 min
        "traffic_duration_sec": 780,  # 13 min (+5 min delay)
        "routes": [
            {
                "route_index": 1,
                "label": "Primary Route (via Ajmer Rd)",
                "description": "Moderate midday commercial flow",
                "distance_km": 3.6,
                "distance_m": 3600,
                "normal_duration_sec": 480,
                "traffic_duration_sec": 780,
                "polyline_coords": [
                    [26.9080, 75.7794], [26.9120, 75.7900], [26.9167, 75.8055]
                ],
            }
        ]
    }
}


def render_demo_mode_view() -> None:
    """Render Offline Presentation Demo Mode."""
    # Prominent Watermark Banner
    st.markdown("""
    <div class="sf-demo-watermark">
        ⚠️ <strong>SIMULATED DEMO DATA (Presentation Only)</strong><br/>
        This scenario demonstrates real-time routing algorithms, risk calculations, and map visualizations 
        offline without requiring an active external API key.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="margin: 0; font-size: 1.6rem; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
            <span>🎬</span> Presentation Demo Mode
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">
            Select a verified simulated scenario to evaluate platform behavior under diverse traffic states.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Scenario Selector
    scenario_name = st.selectbox(
        "Select Presentation Scenario",
        list(DEMO_SCENARIOS.keys()),
        index=0,
    )
    sc = DEMO_SCENARIOS[scenario_name]

    # Calculate real mathematical risk scores for the demo scenario
    parsed_routes = []
    for r in sc["routes"]:
        metrics = compute_route_risk(
            traffic_duration_sec=r["traffic_duration_sec"],
            normal_duration_sec=r["normal_duration_sec"],
            distance_meters=r["distance_m"],
        )
        parsed_routes.append({
            **r,
            **metrics,
        })

    primary = parsed_routes[0]

    # Top status bar
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin: 1.2rem 0; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span class="sf-badge-demo">SIMULATED SCENARIO</span>
            <strong style="color: #F8FAFC; font-size: 1.1rem;">{sc['title']}</strong>
        </div>
        <div style="font-size: 0.8rem; color: #F59E0B;">
            Source: <strong>Simulated Telemetry Cache</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    res_col1, res_col2 = st.columns([1.3, 1.0])
    with res_col1:
        render_risk_gauge_panel(
            risk_score=primary["risk_score"],
            traffic_level=primary["traffic_level"],
            delay_min=primary["delay_min"],
            slowdown_pct=primary["slowdown_pct"],
            title="SIMULATED CORRIDOR RISK SEVERITY",
        )
        render_why_box(primary["reasons"])

    with res_col2:
        st.markdown(f"""
        <div class="sf-glass-panel">
            <div style="font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 0.8rem;">
                ⏱ SIMULATED METRICS
            </div>
            <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(148, 163, 184, 0.1);">
                <span style="color: #94A3B8;">Traffic ETA:</span>
                <strong style="color: #F8FAFC; font-size: 1.05rem;">{primary['eta_min']} min</strong>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(148, 163, 184, 0.1);">
                <span style="color: #94A3B8;">Normal ETA:</span>
                <strong style="color: #94A3B8;">{primary['normal_eta_min']} min</strong>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(148, 163, 184, 0.1);">
                <span style="color: #94A3B8;">Simulated Delay:</span>
                <strong style="color: {primary['level_color']};">+{primary['delay_min']} min</strong>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(148, 163, 184, 0.1);">
                <span style="color: #94A3B8;">Distance:</span>
                <strong style="color: #F8FAFC;">{primary['distance_km']} km</strong>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 6px 0;">
                <span style="color: #94A3B8;">Slowdown:</span>
                <strong style="color: {primary['level_color']};">{primary['slowdown_pct']}%</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💾 Log Demo Run to SQLite History", use_container_width=True):
            log_route_history(
                start_loc=sc["start"],
                dest_loc=sc["dest"],
                distance_km=primary["distance_km"],
                eta_min=primary["eta_min"],
                normal_eta_min=primary["normal_eta_min"],
                delay_min=primary["delay_min"],
                risk_score=primary["risk_score"],
                traffic_level=primary["traffic_level"],
                data_source="DEMO_SIMULATION",
            )
            st.success("Demo scenario logged to audit history.")

    # Alternative routes if present
    if len(parsed_routes) > 1:
        st.markdown("<h3 style='font-size: 1.15rem; margin: 1.5rem 0 0.8rem 0;'>🛣 Alternative Routing Paths</h3>", unsafe_allow_html=True)
        cols = st.columns(len(parsed_routes))
        for i, r in enumerate(parsed_routes):
            is_best = (r["eta_min"] == min(x["eta_min"] for x in parsed_routes))
            with cols[i]:
                st.markdown(f"""
                <div class="sf-route-card {'sf-recommended' if is_best else ''}">
                    <strong style="color: #F8FAFC;">{r['label']}</strong>{' (Fastest)' if is_best else ''}<br/>
                    <span style="font-size: 0.8rem; color: #94A3B8;">{r['description']}</span>
                    <div style="margin-top: 6px; font-size: 0.85rem;">
                        ETA: <strong>{r['eta_min']} min</strong> | Delay: <strong style="color: {r['level_color']};">+{r['delay_min']}m</strong> | Risk: <strong>{r['risk_score']}/100</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Interactive Folium Map
    st.markdown("<h3 style='font-size: 1.15rem; margin: 1.5rem 0 0.8rem 0;'>🗺 Spatial Route Rendering</h3>", unsafe_allow_html=True)
    m = create_traffic_map(
        start_coords=sc["start_coords"],
        dest_coords=sc["dest_coords"],
        routes=parsed_routes,
    )
    st_folium(m, width=None, height=420, returned_objects=[])
