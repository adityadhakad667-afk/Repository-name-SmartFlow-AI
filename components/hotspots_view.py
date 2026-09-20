"""
Traffic Hotspots Component for SmartFlow AI.
Visualizes geographic and network bottlenecks on an interactive map and severity ranking table.

CRITICAL INVARIANT:
Strictly segregates Live Hotspots from Historical Hotspots with clear badges.
"""
from typing import Any, Dict, Optional
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

from analytics.hotspot_engine import get_historical_hotspots, get_live_hotspots
from services.traffic_service import check_live_traffic_status
from .maps import create_traffic_map


def render_hotspots_view(monitored_locations: Optional[list] = None, google_key: Optional[str] = None) -> None:
    """Render Traffic Hotspot Detection screen."""
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="margin: 0; font-size: 1.6rem; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
            <span>🔥</span> Critical Traffic Hotspot Detection
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">
            Identify recurring physical choke points, arterial bottlenecks, and real-time congestion concentrations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    status_info = check_live_traffic_status(google_key=google_key)

    tab_live, tab_historical = st.tabs(["🚦 Live Network Hotspots", "📜 Historical Bottlenecks"])

    with tab_live:
        st.markdown('<span class="sf-badge-live">LIVE TELEMETRY HOTSPOTS</span>', unsafe_allow_html=True)
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        if not status_info["is_connected"]:
            st.info("Live Traffic API is offline. Connect your Google Maps API key in Settings to view dynamic live network hotspots.")
            live_hotspots = []
        elif not monitored_locations:
            st.warning("No locations currently being live-monitored. Go to 'Saved Locations' and click [Refresh All] to populate live hotspots.")
            live_hotspots = []
        else:
            live_hotspots = get_live_hotspots(monitored_locations)

        if live_hotspots:
            col_map, col_table = st.columns([1.2, 1.0])
            with col_map:
                m_live = create_traffic_map(hotspots=live_hotspots, zoom_start=12)
                st_folium(m_live, width=None, height=420, returned_objects=[])

            with col_table:
                df_live = pd.DataFrame(live_hotspots)[["rank", "name", "traffic_level", "current_risk", "delay_min", "updated_at"]]
                df_live.columns = ["Rank", "Corridor Name", "Level", "Risk (0-100)", "Delay (min)", "Last Polled"]
                st.dataframe(df_live, use_container_width=True, hide_index=True)

    with tab_historical:
        st.markdown('<span class="sf-badge-ml">HISTORICAL OBSERVATION DATASET</span>', unsafe_allow_html=True)
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        historical_hotspots = get_historical_hotspots()
        
        col_map2, col_table2 = st.columns([1.2, 1.0])
        with col_map2:
            m_hist = create_traffic_map(hotspots=historical_hotspots, zoom_start=12)
            st_folium(m_hist, width=None, height=420, returned_objects=[])

        with col_table2:
            df_hist = pd.DataFrame(historical_hotspots)[["rank", "name", "road_type", "traffic_level", "average_risk", "average_delay_min", "high_risk_frequency_pct"]]
            df_hist.columns = ["Rank", "Corridor Name", "Road Type", "Level", "Avg Risk", "Avg Delay (min)", "High-Risk Freq %"]
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
