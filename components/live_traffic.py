"""
Live Traffic Route Intelligence Component for SmartFlow AI.
Provides real-time traffic-aware routing using Google Routes API v2,
alternative route comparison, risk classification, and transparent data-backed rationale.

CRITICAL INTEGRITY INVARIANT:
If API key is missing or offline, shows explicit unavailable message.
Never replaces missing live data with fake live values.
"""
from typing import Any, Dict, Optional
import streamlit as st
from streamlit_folium import st_folium

from services.traffic_service import analyze_live_route, check_live_traffic_status
from database.db import log_route_history
from .risk_cards import render_risk_gauge_panel, render_why_box
from .maps import create_traffic_map


def render_live_traffic_view(google_key: Optional[str] = None, tomtom_key: Optional[str] = None) -> None:
    """Render Real-Time Traffic Routing screen."""
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="margin: 0; font-size: 1.6rem; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
            <span>🚦</span> Real-Time Traffic Intelligence & Routing
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">
            Query dynamic Google Routes v2 telemetry with traffic-aware optimal pathing and mathematical risk assessment.
        </p>
    </div>
    """, unsafe_allow_html=True)

    status_info = check_live_traffic_status(google_key=google_key, tomtom_key=tomtom_key)

    # If offline, render clear explanation with link to settings or demo mode
    if not status_info["is_connected"]:
        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #EF4444; font-size: 1.1rem; margin-bottom: 0.5rem;">
                <span>●</span> LIVE TRAFFIC OFFLINE
            </div>
            <p style="color: #E2E8F0; font-size: 0.9rem; line-height: 1.5; margin-bottom: 0.8rem;">
                <strong>Live Traffic is currently unavailable.</strong><br/>
                Configure <code>GOOGLE_MAPS_API_KEY</code> in <strong>Settings</strong> or in your <code>.env</code> file to query live traffic conditions.
            </p>
            <p style="color: #94A3B8; font-size: 0.8rem; margin-bottom: 1rem;">
                In accordance with SmartFlow AI integrity standards, <strong>missing live data is never replaced with fabricated values</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚙ Open Settings to Add API Key", use_container_width=True):
                st.session_state["nav_page"] = "⚙ Settings"
                st.rerun()
        with col2:
            if st.button("🎬 Try Offline Presentation Demo Mode", use_container_width=True):
                st.session_state["nav_page"] = "🎬 Demo Mode"
                st.rerun()
        return

    # If connected, provide live routing interface
    st.markdown('<span class="sf-badge-live">● LIVE TRAFFIC CONNECTED</span>', unsafe_allow_html=True)
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Input Form
    with st.container():
        st.markdown('<div class="sf-glass-panel">', unsafe_allow_html=True)
        col_start, col_dest = st.columns(2)
        with col_start:
            start_input = st.text_input(
                "START LOCATION",
                value=st.session_state.get("lt_start", "Jaipur Railway Station"),
                placeholder="e.g. Jaipur Railway Station, Delhi, New York...",
                help="Type any global landmark, city, or street address",
            )
        with col_dest:
            dest_input = st.text_input(
                "DESTINATION",
                value=st.session_state.get("lt_dest", "Hawa Mahal"),
                placeholder="e.g. Hawa Mahal, Gurgaon, London...",
                help="Type destination address or junction",
            )

        col_pref, col_btn = st.columns([1.5, 1])
        with col_pref:
            preference = st.selectbox(
                "Routing Optimization Preference",
                ["Fastest (Lowest ETA)", "Least Traffic (Lowest Delay)", "Balanced (Optimal Risk & Time)"],
                index=0,
            )
        with col_btn:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            analyze_clicked = st.button("🔍 Analyze Live Route", use_container_width=True, type="primary")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Route execution
    if analyze_clicked or "last_live_result" in st.session_state:
        if analyze_clicked:
            with st.spinner("Connecting to Google Routes API v2 (TRAFFIC_AWARE_OPTIMAL)..."):
                result = analyze_live_route(
                    start_query=start_input,
                    dest_query=dest_input,
                    google_key=google_key,
                    tomtom_key=tomtom_key,
                    preference=preference.split()[0],
                )
                st.session_state["last_live_result"] = result
        else:
            result = st.session_state["last_live_result"]

        if not result.get("success", False):
            st.error(f"Routing Error: {result.get('error', 'Unknown error occurred')}")
            return

        # Display route results
        rec_route = result["recommended_route"] or result["primary_route"]
        routes = result["routes"]

        # Top summary bar
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin: 1.5rem 0 1rem 0; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span class="sf-badge-live">LIVE TRAFFIC</span>
                <span style="color: #F8FAFC; font-weight: 700; font-size: 1.1rem;">
                    {result['start_query']} ➔ {result['dest_query']}
                </span>
            </div>
            <div style="font-size: 0.8rem; color: #94A3B8;">
                Updated: <strong style="color: #38BDF8;">Just now</strong> ({result['timestamp']})
            </div>
        </div>
        """, unsafe_allow_html=True)

        res_cols = st.columns([1.3, 1.0])
        with res_cols[0]:
            render_risk_gauge_panel(
                risk_score=rec_route["risk_score"],
                traffic_level=rec_route["traffic_level"],
                delay_min=rec_route["delay_min"],
                slowdown_pct=rec_route["slowdown_pct"],
                title="REAL-TIME CORRIDOR RISK",
            )
            # WHY Explanation Box
            render_why_box(rec_route["reasons"])

        with res_cols[1]:
            st.markdown(f"""
            <div class="sf-glass-panel">
                <div style="font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 0.8rem;">
                    ⏱ TRIP METRICS BREAKDOWN
                </div>
                <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(148, 163, 184, 0.1);">
                    <span style="color: #94A3B8;">Current Traffic-Aware ETA:</span>
                    <strong style="color: #F8FAFC; font-size: 1.05rem;">{rec_route['eta_min']} min</strong>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(148, 163, 184, 0.1);">
                    <span style="color: #94A3B8;">Normal (Free-Flow) ETA:</span>
                    <strong style="color: #94A3B8;">{rec_route['normal_eta_min']} min</strong>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(148, 163, 184, 0.1);">
                    <span style="color: #94A3B8;">Congestion Delay:</span>
                    <strong style="color: {rec_route['level_color']};">+{rec_route['delay_min']} min</strong>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(148, 163, 184, 0.1);">
                    <span style="color: #94A3B8;">Corridor Distance:</span>
                    <strong style="color: #F8FAFC;">{rec_route['distance_km']} km</strong>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 6px 0;">
                    <span style="color: #94A3B8;">Slowdown Percentage:</span>
                    <strong style="color: {rec_route['level_color']};">{rec_route['slowdown_pct']}%</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("💾 Save Route to Audit History", use_container_width=True):
                log_route_history(
                    start_loc=result["start_query"],
                    dest_loc=result["dest_query"],
                    distance_km=rec_route["distance_km"],
                    eta_min=rec_route["eta_min"],
                    normal_eta_min=rec_route["normal_eta_min"],
                    delay_min=rec_route["delay_min"],
                    risk_score=rec_route["risk_score"],
                    traffic_level=rec_route["traffic_level"],
                    data_source="LIVE",
                )
                st.success("Route logged to SQLite history.")

        # Alternative Routes Section
        if len(routes) > 1:
            st.markdown("<h3 style='font-size: 1.15rem; margin: 1.5rem 0 0.8rem 0;'>🛣 Route Options Comparison</h3>", unsafe_allow_html=True)
            alt_cols = st.columns(len(routes))
            for i, r in enumerate(routes):
                is_best = (r == rec_route)
                card_class = "sf-route-card sf-recommended" if is_best else "sf-route-card"
                badge = " ⭐ RECOMMENDED" if is_best else ""
                with alt_cols[i]:
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                            <strong style="color: #F8FAFC;">{r['label']}{badge}</strong>
                            <span style="color: {r['level_color']}; font-weight: bold;">{r['traffic_level']}</span>
                        </div>
                        <div style="font-size: 0.8rem; color: #94A3B8; margin-bottom: 6px;">{r['description']}</div>
                        <div style="font-size: 0.85rem; line-height: 1.6;">
                            ETA: <strong style="color: #F8FAFC;">{r['eta_min']} min</strong><br/>
                            Delay: <strong style="color: {r['level_color']};">+{r['delay_min']} min</strong><br/>
                            Distance: <strong>{r['distance_km']} km</strong><br/>
                            Risk Score: <strong style="color: {r['level_color']};">{r['risk_score']}/100</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Interactive Folium Map
        st.markdown("<h3 style='font-size: 1.15rem; margin: 1.5rem 0 0.8rem 0;'>🗺 Live Route Spatial Map</h3>", unsafe_allow_html=True)
        route_map = create_traffic_map(
            start_coords=result["start_coords"],
            dest_coords=result["dest_coords"],
            routes=routes,
        )
        st_folium(route_map, width=None, height=450, returned_objects=[])
