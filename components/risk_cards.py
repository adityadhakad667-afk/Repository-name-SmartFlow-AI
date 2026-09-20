"""
Risk and Metric Card Components for SmartFlow AI.
Renders KPI cards, risk meters, and strictly separates confidence from risk scores.
"""
from typing import Any, Dict, List, Optional
import streamlit as st


def render_kpi_card(
    label: str,
    value: str,
    icon: str = "📊",
    subtext: str = "",
    color: str = "#38BDF8",
) -> None:
    """Render a modern dark glassmorphic KPI card with hover animation."""
    st.markdown(f"""
    <div class="sf-kpi-card">
        <div class="sf-kpi-label">
            <span>{icon}</span> {label}
        </div>
        <div class="sf-kpi-value" style="color: {color};">
            {value}
        </div>
        <div class="sf-kpi-subtext">
            {subtext}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_status_banner(status_info: Dict[str, Any]) -> None:
    """Render top system connectivity status banner."""
    is_live = status_info.get("is_connected", False)
    status_text = status_info.get("status_text", "● LIVE TRAFFIC OFFLINE")
    provider = status_info.get("provider", "None")
    
    if is_live:
        badge_html = f'<span class="sf-badge-live">{status_text}</span>'
    else:
        badge_html = f'<span class="sf-badge-offline">{status_text}</span>'

    st.html(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.2rem; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            {badge_html}
            <span style="font-size: 0.8rem; color: #94A3B8;">Provider: <strong style="color: #F8FAFC;">{provider}</strong></span>
        </div>
        <div style="font-size: 0.75rem; color: #64748B;">
            SmartFlow Core Engine v2.4
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_risk_gauge_panel(
    risk_score: int,
    traffic_level: str,
    confidence_pct: Optional[float] = None,
    delay_min: Optional[float] = None,
    slowdown_pct: Optional[float] = None,
    title: str = "CONGESTION RISK ANALYSIS",
) -> None:
    """
    Renders risk score and level with an animated progress bar.
    STRICT INVARIANT:
    Confidence (if provided) is presented as a separate statistical metric,
    never confused with the physical risk score.
    """
    if risk_score < 40:
        color = "#10B981"
        badge_class = "sf-risk-pill-low"
    elif risk_score < 70:
        color = "#F59E0B"
        badge_class = "sf-risk-pill-medium"
    else:
        color = "#EF4444"
        badge_class = "sf-risk-pill-high"

    confidence_block = ""
    if confidence_pct is not None:
        confidence_block = f"""
        <div style="background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 8px; padding: 0.6rem 1rem; text-align: center;">
            <div style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">Model Confidence</div>
            <div style="font-size: 1.3rem; font-weight: 700; color: #38BDF8;">{confidence_pct}%</div>
            <div style="font-size: 0.65rem; color: #64748B;">Classification certainty</div>
        </div>
        """

     delay_block = ""
    if delay_min is not None:
        delay_str = f"+{delay_min} min" if delay_min > 0 else "0 min"
        delay_block = f"""
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 0.6rem 1rem; text-align: center;">
            <div style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">Traffic Delay</div>
            <div style="font-size: 1.3rem; font-weight: 700; color: {color};">{delay_str}</div>
            <div style="font-size: 0.65rem; color: #64748B;">Over free flow</div>
        </div>
        """

    slowdown_block = ""
    if slowdown_pct is not None:
        slowdown_block = f"""
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 0.6rem 1rem; text-align: center;">
            <div style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">Speed Slowdown</div>
            <div style="font-size: 1.3rem; font-weight: 700; color: {color};">{slowdown_pct}%</div>
            <div style="font-size: 0.65rem; color: #64748B;">Speed deficit</div>
        </div>
        """

    st.html(f"""
    <div class="sf-glass-panel">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div style="font-size: 0.85rem; font-weight: 700; letter-spacing: 0.08em; color: #94A3B8; text-transform: uppercase;">
                {title}
            </div>
            <div>
                <span class="{badge_class}">{traffic_level} CONGESTION</span>
            </div>
        </div>

        <div style="display: flex; align-items: baseline; gap: 8px; margin-bottom: 0.5rem;">
            <span style="font-size: 3rem; font-weight: 800; color: {color}; line-height: 1;">{risk_score}</span>
            <span style="font-size: 1.1rem; color: #64748B; font-weight: 600;">/ 100</span>
            <span style="margin-left: auto; font-size: 0.8rem; color: #94A3B8;">Severity Index</span>
        </div>

        <!-- Progress bar track -->
        <div style="background: rgba(148, 163, 184, 0.15); height: 10px; border-radius: 9999px; overflow: hidden; margin-bottom: 1.25rem;">
            <div style="background: {color}; width: {risk_score}%; height: 100%; border-radius: 9999px; box-shadow: 0 0 10px {color}; transition: width 0.6s ease;"></div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px;">
            {delay_block}
            {slowdown_block}
            {confidence_block}
        </div>
    </div>
    """)


def render_why_box(reasons: List[str]) -> None:
    """Render transparent data-supported WHY explanation box."""
    if not reasons:
        return

    items_html = "".join([f'<li style="margin-bottom: 6px; color: #E2E8F0;">{r}</li>' for r in reasons])

    st.markdown(f"""
    <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 10px; padding: 1.1rem 1.4rem; margin-top: 1rem;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #38BDF8; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.6rem; display: flex; align-items: center; gap: 6px;">
            <span>🧠</span> WHY THIS EVALUATION?
        </div>
        <ul style="margin: 0; padding-left: 1.2rem; font-size: 0.85rem; line-height: 1.5;">
            {items_html}
        </ul>
    </div>
    """)
