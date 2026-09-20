"""
Audit History View Component for SmartFlow AI.
Displays historical analyzed routes stored in SQLite, with search filters, CSV export, and record management.
"""
from typing import Any, Dict
import streamlit as st
import pandas as pd

from database.db import get_route_history, clear_route_history


def render_history_view() -> None:
    """Render route audit history screen."""
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="margin: 0; font-size: 1.6rem; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
            <span>📜</span> Route Analysis Audit History
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">
            Query, filter, and export historical route analyses recorded to local SQLite storage.
        </p>
    </div>
    """, unsafe_allow_html=True)

    records = get_route_history(limit=250)

    if not records:
        st.info("No route queries logged yet. Analyze a route in 'Live Traffic' or run a scenario in 'Demo Mode' to log records.")
        return

    df_hist = pd.DataFrame(records)

    # Top Action Row
    col_filter, col_export, col_clear = st.columns([2, 1, 1])
    with col_filter:
        level_filter = st.multiselect(
            "Filter by Congestion Severity",
            options=["LOW", "MEDIUM", "HIGH"],
            default=["LOW", "MEDIUM", "HIGH"],
        )
    with col_export:
        csv_data = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export History (CSV)",
            data=csv_data,
            file_name="smartflow_route_history.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_clear:
        if st.button("🗑 Clear Audit History", use_container_width=True):
            clear_route_history()
            st.success("History successfully cleared.")
            st.rerun()

    # Filtered View
    filtered_df = df_hist[df_hist["traffic_level"].isin(level_filter)]

    st.markdown(f"<div style='font-size: 0.85rem; color: #94A3B8; margin: 10px 0;'>Showing {len(filtered_df)} records:</div>", unsafe_allow_html=True)

    display_cols = ["timestamp", "start_loc", "dest_loc", "distance_km", "eta_min", "normal_eta_min", "delay_min", "risk_score", "traffic_level", "data_source"]
    clean_df = filtered_df[display_cols].copy()
    clean_df.columns = ["Timestamp", "Origin", "Destination", "Distance (km)", "ETA (min)", "Normal ETA", "Delay (min)", "Risk Score", "Level", "Source"]

    st.dataframe(clean_df, use_container_width=True, hide_index=True)
