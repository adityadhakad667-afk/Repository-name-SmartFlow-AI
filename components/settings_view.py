"""
Settings View Component for SmartFlow AI.
Manages API key configurations, polling refresh intervals, map themes,
and test connection diagnostics.
"""
import os
from typing import Any, Dict
import streamlit as st

from database.db import get_setting, set_setting
from services.traffic_service import check_live_traffic_status
from services.routing_service import fetch_google_routes


def render_settings_view() -> None:
    """Render application settings and diagnostics interface."""
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="margin: 0; font-size: 1.6rem; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
            <span>⚙</span> Platform Settings & API Configuration
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">
            Configure external telemetry keys, refresh cadence, and visual presentation styles.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1. API Keys Management
    st.markdown('<div class="sf-glass-panel">', unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 1.1rem; margin-top: 0; color: #38BDF8;'>🔑 Telemetry Provider API Keys</h3>", unsafe_allow_html=True)
    
    current_google_key = st.session_state.get("google_api_key", os.environ.get("GOOGLE_MAPS_API_KEY", ""))
    current_tomtom_key = st.session_state.get("tomtom_api_key", os.environ.get("TOMTOM_API_KEY", ""))

    with st.form("api_keys_form"):
        new_google_key = st.text_input(
            "Google Maps Platform API Key",
            value=current_google_key,
            type="password",
            help="Requires Google Routes API (v2) and Geocoding API enabled.",
        )
        new_tomtom_key = st.text_input(
            "TomTom Routing & Traffic Flow API Key (Optional Alternative)",
            value=current_tomtom_key,
            type="password",
            help="Optional secondary provider fallback.",
        )
        save_keys = st.form_submit_button("Save & Update Active Keys")

        if save_keys:
            st.session_state["google_api_key"] = new_google_key.strip()
            st.session_state["tomtom_api_key"] = new_tomtom_key.strip()
            os.environ["GOOGLE_MAPS_API_KEY"] = new_google_key.strip()
            os.environ["TOMTOM_API_KEY"] = new_tomtom_key.strip()
            set_setting("GOOGLE_MAPS_API_KEY", new_google_key.strip())
            set_setting("TOMTOM_API_KEY", new_tomtom_key.strip())
            st.success("API Keys updated for current session and stored in local settings.")
            st.rerun()

    # Diagnostics / Test Connection Button
    col_diag, col_status = st.columns([1, 2])
    with col_diag:
        if st.button("🔌 Test API Connection", use_container_width=True):
            if not new_google_key:
                st.warning("No Google Maps API key provided to test.")
            else:
                with st.spinner("Testing Google Routes v2 connection..."):
                    test_res = fetch_google_routes(
                        origin_lat=26.9196, origin_lon=75.7878,
                        dest_lat=26.9239, dest_lon=75.8267,
                        api_key=new_google_key,
                    )
                    if test_res["status"] == "CONNECTED":
                        st.success("✅ Google Routes API v2 is online and verified!")
                    else:
                        st.error(f"❌ Connection failed: {test_res.get('error')}")

    with col_status:
        status_info = check_live_traffic_status(google_key=new_google_key, tomtom_key=new_tomtom_key)
        st.markdown(f"Current Status: **{status_info['status_text']}** ({status_info['provider']})")

    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Preferences & Map Styling
    st.markdown('<div class="sf-glass-panel">', unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 1.1rem; margin-top: 0; color: #38BDF8;'>🎨 Interface & Telemetry Preferences</h3>", unsafe_allow_html=True)

    c_theme, c_refresh, c_map = st.columns(3)
    with c_theme:
        st.selectbox("UI Theme", ["Dark Command Center (Obsidian/Cyan)", "High Contrast Navy"], index=0)
    with c_refresh:
        refresh_choice = st.selectbox("Live Monitor Auto-Refresh", ["Manual Only", "Every 30 Seconds", "Every 60 Seconds"], index=0)
        st.session_state["auto_refresh_setting"] = refresh_choice
    with c_map:
        tile_choice = st.selectbox(
            "Default Map Tile Style",
            ["CartoDB dark_matter", "CartoDB positron", "OpenStreetMap"],
            index=0,
        )
        st.session_state["map_tile_theme"] = tile_choice

    st.markdown('</div>', unsafe_allow_html=True)
