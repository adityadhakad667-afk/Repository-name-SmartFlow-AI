# SmartFlow AI: AI-Powered Real-Time Traffic Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-red.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/ML-RandomForest%20%26%20XGBoost-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

> **"Predict. Monitor. Understand. Optimize."**

SmartFlow AI is an enterprise-grade, commercial-ready traffic intelligence command center. Built entirely from scratch with a modular service-oriented architecture, SmartFlow AI integrates **real-time physical road telemetry** (via Google Routes API v2) with **multivariate predictive Machine Learning ensembles** (Random Forest & XGBoost) and a rigorous **0–100 Congestion Severity Risk Engine**.

---

## 🌟 Key Platform Features

1. **Real-Time Traffic Intelligence**:
   - Live query of any global route (Start & Destination resolved by geocoding).
   - Real-time traffic-aware durations (`TRAFFIC_AWARE_OPTIMAL`) versus free-flow baselines.
   - Dynamic delays, slowdown percentages, and data-backed "WHY?" explanations.
2. **Alternative Route Comparison & Optimization**:
   - Compare up to 3 parallel driving routes with individual risk profiles.
   - User-controlled routing preferences: **Fastest (Lowest ETA)**, **Least Traffic (Lowest Delay)**, or **Balanced (Optimal Risk & Time)**.
3. **Rigorous Traffic Risk Scoring (0–100)**:
   - Formulated mathematically from delay ratios, velocity slowdowns, and road capacities.
   - Categorized cleanly into **LOW (0–39)**, **MEDIUM (40–69)**, and **HIGH (70–100)**.
   - **Strict Invariant**: Model confidence is isolated from congestion risk (e.g. 99% confidence of LOW traffic reports `LOW (20/100, 99% confidence)`).
4. **Machine Learning Congestion Prediction**:
   - Trained ensemble comparing Random Forest (94.4% F1) and XGBoost (94.0% F1).
   - Multi-factor inference factoring diurnal rush hours, weather, temperature, precipitation, and vehicle densities.
5. **Predictive 3h & 6h Forward Forecasting**:
   - Multi-hour forward trajectory modeling with uncertainty bounds, explicitly labeled `MODEL FORECAST`.
6. **Hotspot Detection Engine**:
   - Segregated into **Live Telemetry Hotspots** (from monitored nodal points) and **Historical Corridors** (aggregated from observations).
7. **Transparent Explainable AI (XAI)**:
   - Tree split feature importance breakdowns (Vehicle Density: ~46.5%, Hour: ~22.8%, Weather: ~9.4%).
   - Contextual natural language explanations detailing the primary factors behind each forecast.
8. **Persistent SQLite Storage**:
   - Saved nodal monitoring locations (dynamic real-time status; no hardcoded static labels).
   - Route query audit history logging with single-click CSV export.
9. **Zero-API Presentation Demo Mode**:
   - Offline presentation scenarios with explicit watermark: `⚠️ SIMULATED DEMO DATA (Presentation Only)`.
10. **Investor Presentation Deck**:
    - Executive problem-solution breakdown, market impact, real-time KPI aggregations, and visual end-to-end data flow architecture.

---

## 🏗 System Architecture

```
                                  ┌───────────────────────────┐
                                  │   Real-Time Data Sources  │
                                  │ (Google Routes API v2 /   │
                                  │   TomTom / Open-Meteo)    │
                                  └─────────────┬─────────────┘
                                                │
                                                ▼
                                  ┌───────────────────────────┐
                                  │      Traffic Service      │
                                  │ (Telemetry & Geocoding)   │
                                  └─────────────┬─────────────┘
                                                │
                                                ▼
┌───────────────────────────┐     ┌───────────────────────────┐
│   Machine Learning Hub    │────▶│     Risk & XAI Engine     │
│ (Random Forest & XGBoost) │     │ (0–100 Risk & Rationale)  │
└───────────────────────────┘     └─────────────┬─────────────┘
                                                │
                                                ▼
                                  ┌───────────────────────────┐
                                  │   Smart Routing Advisory  │
                                  │ (Multi-path Optimization) │
                                  └─────────────┬─────────────┘
                                                │
                                                ▼
                                  ┌───────────────────────────┐
                                  │ Dark Glassmorphism UI     │
                                  │ (Streamlit, Folium,       │
                                  │   Plotly, SQLite)         │
                                  └───────────────────────────┘
```

---

## 📂 Project Directory Structure

```
SmartFlow-AI/
├── app.py                      # Main Streamlit application entry point & router
├── requirements.txt            # Python dependencies
├── README.md                   # Platform documentation & operational manual
├── .env.example                # Template configuration file for secrets
├── .gitignore                  # Git ignore rules for credentials, DB, and cache
│
├── services/                   # External Telemetry & Geolocation Services
│   ├── geocoding_service.py    # Google Geocoding with OpenStreetMap fallback
│   ├── routing_service.py      # Google Routes API (v2) traffic-aware routes & polylines
│   ├── traffic_service.py      # Live status checker and batch monitor orchestrator
│   └── weather_service.py      # Open-Meteo ambient weather integration
│
├── ml/                         # Machine Learning Pipeline
│   ├── preprocessing.py        # Realistic synthetic dataset generator & preprocessing
│   ├── train.py                # Train/test split, RF vs XGBoost evaluation & serialization
│   ├── predict.py              # Real-time multi-factor inference & confidence extraction
│   └── model.py                # Model container and Explainable AI feature attribution
│
├── analytics/                  # Algorithmic Scoring & Analytical Engines
│   ├── risk_engine.py          # 0–100 risk formula, tier thresholds, data-backed reasons
│   ├── forecasting.py          # 3h and 6h forward temporal predictive projections
│   └── hotspot_engine.py       # Live probe and historical bottleneck identification
│
├── database/                   # SQLite Persistence Layer
│   ├── db.py                   # Schema initialization, saved locations, route history
│   └── smartflow.db            # Auto-created SQLite runtime database
│
├── components/                 # UI Views & Presentation Components
│   ├── styles.py               # Dark Glassmorphism CSS design system
│   ├── sidebar.py              # Navigation bar with live status badge
│   ├── dashboard.py            # Central command center landing view with live KPIs
│   ├── live_traffic.py         # Live routing, ETA comparison & alternative routes
│   ├── maps.py                 # Leaflet/Folium dark interactive map renderer
│   ├── charts.py               # Plotly dark interactive data visualizations
│   ├── risk_cards.py           # Glassmorphic KPI cards and animated risk meters
│   ├── ai_prediction.py        # Interactive ML feature prediction interface
│   ├── forecast_view.py        # Forward-looking timeline chart and hourly forecast
│   ├── hotspots_view.py        # Spatial hotspot map and ranking tables
│   ├── explainable_ai.py       # Feature attribution rankings and AI insights
│   ├── analytics_view.py       # Multi-dimensional analytics charts
│   ├── saved_locations.py      # Saved locations CRUD and dynamic live monitor
│   ├── history_view.py         # SQLite route query audit table & CSV export
│   ├── demo_mode.py            # Offline simulation scenarios for presentations
│   ├── investor_view.py        # Executive pitch deck & architectural flow
│   └── settings_view.py        # Telemetry API keys & preference controls
│
├── data/                       # Historical Datasets
│   └── sample_traffic_data.csv # 5,000 multi-factor traffic observation dataset
│
├── models/                     # Serialized Model Artifacts
│   ├── traffic_classifier.joblib
│   └── model_metadata.json
│
└── tests/                      # Automated Verification Test Suite
    ├── test_database.py        # SQLite CRUD and schema tests
    ├── test_risk_engine.py     # Risk formulas and confidence isolation tests
    ├── test_routing_service.py # Routing fallback and polyline decoder tests
    └── test_ml_pipeline.py     # Model inference and explainability tests
```

---

## 🛠 Technology Stack

- **Frontend**: Streamlit 1.63+, Custom Dark Glassmorphism CSS, Plotly 7.0+, Folium 0.20+, streamlit-folium.
- **Backend**: Python 3.10+.
- **Data Engineering**: Pandas 3.0+, NumPy 2.5+.
- **Machine Learning**: Scikit-Learn 1.9+, XGBoost 3.4+, Joblib.
- **Live Telemetry & GIS**: Google Routes API (v2), Google Geocoding API, OpenStreetMap Nominatim, Open-Meteo.
- **Persistence**: SQLite 3.

---

## 🚀 Installation & Local Execution

### 1. Prerequisites
Ensure Python 3.10 or higher is installed:
```bash
python --version
```

### 2. Navigate to the Project Directory
```bash
cd C:\Users\lenovo\.gemini\antigravity\scratch\SmartFlow-AI
```

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Configure API Keys (Optional for Live Telemetry)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and set your key:
```env
GOOGLE_MAPS_API_KEY=your_actual_google_maps_api_key_here
```
> *Note: If no API key is provided, SmartFlow AI runs gracefully in offline mode, displaying `● LIVE TRAFFIC OFFLINE`. You can test full functionality offline via **Demo Mode** or the **AI Prediction Engine**.*

### 5. Launch the Streamlit Platform
```bash
python -m streamlit run app.py
```
Open your browser and navigate to:
```
http://localhost:8501
```

---

## 🔑 Telemetry API Configuration

To enable **Live Traffic Routing**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and enable:
   - **Routes API** (Directions v2)
   - **Geocoding API**
3. Generate an API Key and restrict it as needed.
4. Input your key into the **⚙ Settings** screen inside the app or in your `.env` file.
5. Click **🔌 Test API Connection** in Settings to verify live handshake.

---

## 🧪 Running Automated Tests

Run the test suite:
```bash
python -m unittest discover tests
```
Current test suite covers:
- Zero delay yielding 0 risk.
- Severe delay yielding HIGH risk (>70).
- Strict isolation verifying 99% confidence does not equal 99/100 risk score.
- SQLite schema generation, CRUD, and KPI aggregation.
- Google encoded polyline decoding.
- Offline routing fallback without throwing unhandled exceptions.
- ML pipeline inference contract and feature contributions.

---

## ⚠️ Known Limitations & Integrity Guardrails

- **No Fabricated Live Data**: SmartFlow AI strictly adheres to data integrity. If no Google Maps API key is configured or network is unavailable, live telemetry reports `Live data unavailable` or `● LIVE TRAFFIC OFFLINE`. It will never inject fake values into real-time views.
- **Demo Mode Distinction**: All simulated demo scenarios are watermarked with `⚠️ SIMULATED DEMO DATA (Presentation Only)` to prevent misrepresenting simulation as real-time GPS telemetry.
- **Google Cloud Quotas**: Free-tier Google Maps keys are subject to standard rate limits (e.g. 100 requests/second).
