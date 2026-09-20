"""
Design System and Dark Glassmorphism CSS for SmartFlow AI.
Implements modern traffic command center aesthetics: deep obsidian/navy backgrounds,
subtle cyan glowing accents, glass card backdrops, and high-contrast typography.
"""

CUSTOM_CSS = """
<style>
/* =======================================================
   SMARTFLOW AI - DARK GLASSMORHISM DESIGN SYSTEM
   ======================================================= */

:root {
    --bg-main: #070B14;
    --bg-card: rgba(15, 23, 42, 0.75);
    --bg-card-hover: rgba(30, 41, 59, 0.85);
    --border-card: rgba(56, 189, 248, 0.15);
    --border-card-hover: rgba(56, 189, 248, 0.40);
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
    --cyan-accent: #06B6D4;
    --cyan-glow: rgba(6, 182, 212, 0.25);
    --blue-accent: #38BDF8;
    --risk-low: #10B981;
    --risk-med: #F59E0B;
    --risk-high: #EF4444;
}

/* Overall background & text */
.stApp {
    background: radial-gradient(circle at 10% 10%, #0F172A 0%, #070B14 80%, #030712 100%) !important;
    color: var(--text-primary) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: rgba(11, 17, 32, 0.95) !important;
    border-right: 1px solid rgba(56, 189, 248, 0.12) !important;
    backdrop-filter: blur(12px);
}

[data-testid="stSidebar"] hr {
    border-color: rgba(148, 163, 184, 0.15) !important;
    margin: 1rem 0 !important;
}

/* Hide default streamlit header/footer decorations */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {background: transparent !important;}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    color: #F8FAFC !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

/* Custom header block */
.sf-brand-header {
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid rgba(56, 189, 248, 0.15);
}

.sf-brand-title {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    background: linear-gradient(135deg, #FFFFFF 30%, #38BDF8 70%, #06B6D4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
    margin: 0;
}

.sf-brand-subtitle {
    color: #94A3B8;
    font-size: 0.95rem;
    margin-top: 0.2rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Glassmorphic Metric / KPI Card */
.sf-kpi-card {
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(56, 189, 248, 0.15);
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    backdrop-filter: blur(10px);
    transition: all 0.25s ease-in-out;
    margin-bottom: 1rem;
}

.sf-kpi-card:hover {
    transform: translateY(-2px);
    border-color: rgba(56, 189, 248, 0.45);
    box-shadow: 0 8px 30px rgba(6, 182, 212, 0.15);
}

.sf-kpi-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #94A3B8;
    font-weight: 600;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.sf-kpi-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: #F8FAFC;
    line-height: 1.1;
}

.sf-kpi-subtext {
    font-size: 0.75rem;
    color: #64748B;
    margin-top: 0.35rem;
}

/* Glass Card generic container */
.sf-glass-panel {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(56, 189, 248, 0.15);
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
    backdrop-filter: blur(12px);
    margin-bottom: 1.5rem;
}

/* Status Badges */
.sf-badge-live {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #10B981;
    padding: 0.3rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.sf-badge-offline {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: #EF4444;
    padding: 0.3rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.sf-badge-ml {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid rgba(56, 189, 248, 0.4);
    color: #38BDF8;
    padding: 0.3rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.sf-badge-demo {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid rgba(245, 158, 11, 0.4);
    color: #F59E0B;
    padding: 0.3rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}

/* Watermark banner for Demo Mode */
.sf-demo-watermark {
    background: linear-gradient(90deg, rgba(245, 158, 11, 0.2) 0%, rgba(245, 158, 11, 0.05) 100%);
    border-left: 4px solid #F59E0B;
    padding: 0.75rem 1.25rem;
    border-radius: 0 8px 8px 0;
    color: #FCD34D;
    font-weight: 600;
    margin-bottom: 1.2rem;
    font-size: 0.85rem;
}

/* Risk Score Gauge Pills */
.sf-risk-pill-low {
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
    border: 1px solid rgba(16, 185, 129, 0.35);
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.8rem;
}

.sf-risk-pill-medium {
    background: rgba(245, 158, 11, 0.15);
    color: #F59E0B;
    border: 1px solid rgba(245, 158, 11, 0.35);
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.8rem;
}

.sf-risk-pill-high {
    background: rgba(239, 68, 68, 0.15);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.35);
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.8rem;
}

/* Form controls styling */
.stTextInput > div > div > input,
.stSelectbox > div > div > div {
    background-color: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid rgba(56, 189, 248, 0.2) !important;
    color: #F8FAFC !important;
    border-radius: 8px !important;
}

.stTextInput > div > div > input:focus {
    border-color: #38BDF8 !important;
    box-shadow: 0 0 0 1px #38BDF8 !important;
}

/* Streamlit buttons */
.stButton > button {
    background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    padding: 0.5rem 1.25rem !important;
    transition: all 0.2s ease-in-out !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%) !important;
    border-color: #38BDF8 !important;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.35) !important;
    transform: translateY(-1px) !important;
}

/* Streamlit tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: rgba(15, 23, 42, 0.6) !important;
    border-radius: 8px;
    padding: 4px;
    gap: 6px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 6px !important;
    color: #94A3B8 !important;
    padding: 8px 16px !important;
    font-weight: 600 !important;
}

.stTabs [aria-selected="true"] {
    background-color: rgba(56, 189, 248, 0.18) !important;
    color: #38BDF8 !important;
}

/* Route alternative card */
.sf-route-card {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 10px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    transition: all 0.2s ease;
}

.sf-route-card:hover {
    border-color: rgba(56, 189, 248, 0.5);
    background: rgba(20, 30, 55, 0.9);
}

.sf-route-card.sf-recommended {
    border: 1px solid #10B981 !important;
    background: rgba(16, 185, 129, 0.08) !important;
}
</style>
"""
