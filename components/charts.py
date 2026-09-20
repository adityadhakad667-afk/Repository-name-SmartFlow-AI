"""
Plotly Data Visualization Components for SmartFlow AI.
Generates dark-styled responsive charts matching the command center aesthetic.
"""
from typing import Any, Dict, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Consistent dark chart layout
DARK_LAYOUT = {
    "paper_bgcolor": "rgba(15, 23, 42, 0.0)",
    "plot_bgcolor": "rgba(15, 23, 42, 0.4)",
    "font": {"color": "#94A3B8", "family": "Segoe UI, sans-serif"},
    "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
    "xaxis": {
        "gridcolor": "rgba(148, 163, 184, 0.1)",
        "zerolinecolor": "rgba(148, 163, 184, 0.2)",
    },
    "yaxis": {
        "gridcolor": "rgba(148, 163, 184, 0.1)",
        "zerolinecolor": "rgba(148, 163, 184, 0.2)",
    },
}


def plot_forecast_timeline(points: List[Dict[str, Any]]) -> go.Figure:
    """Render 3h/6h risk and vehicle density forecast line chart."""
    df = pd.DataFrame(points)
    
    fig = go.Figure()

    # Risk score line
    fig.add_trace(
        go.Scatter(
            x=df["forecast_time"],
            y=df["risk_score"],
            mode="lines+markers",
            name="Risk Score (0-100)",
            line={"color": "#38BDF8", "width": 3},
            marker={"size": 8, "color": "#0284C7", "line": {"width": 2, "color": "#FFFFFF"}},
        )
    )

    # Threshold horizontal reference lines
    fig.add_hline(y=70, line_dash="dash", line_color="#EF4444", annotation_text="High Risk Threshold (70)", annotation_position="bottom right")
    fig.add_hline(y=40, line_dash="dash", line_color="#F59E0B", annotation_text="Medium Risk Threshold (40)", annotation_position="bottom right")

    fig.update_layout(
        **DARK_LAYOUT,
        title={"text": "🔮 Projected Congestion Risk Score Over Time", "font": {"color": "#F8FAFC", "size": 15}},
        yaxis_title="Risk Score (0–100)",
        xaxis_title="Forecast Window",
        yaxis_range=[0, 105],
        hovermode="x unified",
    )
    return fig


def plot_feature_importances(importances: Dict[str, float]) -> go.Figure:
    """Render horizontal bar chart for Explainable AI feature importances."""
    readable = {
        "vehicle_count": "Vehicle Count (Density)",
        "hour": "Hour of Day (Peak Factors)",
        "weather": "Weather Condition",
        "road_type": "Road Hierarchy",
        "precipitation": "Precipitation Rate",
        "temperature": "Ambient Temperature",
        "day_of_week": "Day of Week",
        "free_flow_speed": "Design Free-Flow Speed",
    }
    
    items = sorted(importances.items(), key=lambda x: x[1])
    labels = [readable.get(k, k.replace("_", " ").title()) for k, _ in items]
    values = [v * 100 for _, v in items]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker={
                "color": values,
                "colorscale": [[0, "#0284C7"], [0.5, "#06B6D4"], [1, "#38BDF8"]],
            },
            text=[f"{v:.1f}%" for v in values],
            textposition="outside",
        )
    )

    fig.update_layout(
        **DARK_LAYOUT,
        title={"text": "🧠 Model Feature Importance Weights", "font": {"color": "#F8FAFC", "size": 15}},
        xaxis_title="Feature Influence (%)",
        yaxis_title="",
        xaxis_range=[0, max(values) * 1.25 if values else 100],
    )
    return fig


def plot_hourly_traffic_trends(df: pd.DataFrame) -> go.Figure:
    """Render diurnal traffic trends (Vehicles & Avg Speed by Hour)."""
    hourly = df.groupby("hour").agg({"vehicle_count": "mean", "avg_speed": "mean"}).reset_index()

    fig = go.Figure()
    # Vehicle count bar
    fig.add_trace(
        go.Bar(
            x=hourly["hour"],
            y=hourly["vehicle_count"],
            name="Vehicles / Hr",
            marker_color="rgba(56, 189, 248, 0.4)",
            yaxis="y",
        )
    )
    # Average speed line
    fig.add_trace(
        go.Scatter(
            x=hourly["hour"],
            y=hourly["avg_speed"],
            name="Avg Speed (km/h)",
            mode="lines+markers",
            line={"color": "#10B981", "width": 3},
            yaxis="y2",
        )
    )

    fig.update_layout(
        **DARK_LAYOUT,
        title={"text": "⏱ Average Vehicle Volume & Velocity by Hour", "font": {"color": "#F8FAFC", "size": 15}},
        xaxis_title="Hour of Day (0-23)",
        yaxis={"title": "Vehicle Volume", "gridcolor": "rgba(148, 163, 184, 0.1)"},
        yaxis2={
            "title": "Speed (km/h)",
            "overlaying": "y",
            "side": "right",
            "gridcolor": "rgba(16, 185, 129, 0.05)",
        },
        legend={"orientation": "h", "y": 1.15, "x": 0.3},
    )
    return fig


def plot_risk_distribution(df: pd.DataFrame) -> go.Figure:
    """Render risk score histogram across dataset."""
    fig = px.histogram(
        df,
        x="risk_score",
        nbins=25,
        color="congestion_level",
        color_discrete_map={"LOW": "#10B981", "MEDIUM": "#F59E0B", "HIGH": "#EF4444"},
        labels={"risk_score": "Risk Score (0–100)", "congestion_level": "Congestion Level"},
    )
    fig.update_layout(
        **DARK_LAYOUT,
        title={"text": "📊 Distribution of Historical Congestion Risk Scores", "font": {"color": "#F8FAFC", "size": 15}},
        yaxis_title="Observation Count",
        barmode="stack",
    )
    return fig


def plot_model_comparison(comparison_data: Dict[str, Dict[str, float]]) -> go.Figure:
    """Render grouped bar chart comparing Random Forest vs XGBoost."""
    metrics = ["accuracy", "precision", "recall", "f1_score"]
    metric_labels = ["Accuracy", "Precision", "Recall", "F1 Score"]

    rf_scores = [comparison_data.get("Random Forest", {}).get(m, 0.0) for m in metrics]
    xgb_scores = [comparison_data.get("XGBoost", {}).get(m, 0.0) for m in metrics]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=metric_labels, y=rf_scores, name="Random Forest", marker_color="#0284C7"))
    fig.add_trace(go.Bar(x=metric_labels, y=xgb_scores, name="XGBoost", marker_color="#38BDF8"))

    fig.update_layout(
        **DARK_LAYOUT,
        title={"text": "🤖 ML Model Architecture Evaluation (Train/Test Split)", "font": {"color": "#F8FAFC", "size": 15}},
        yaxis_title="Score (0.0 – 1.0)",
        yaxis_range=[0.75, 1.02],
        barmode="group",
        legend={"orientation": "h", "y": 1.15, "x": 0.3},
    )
    return fig
