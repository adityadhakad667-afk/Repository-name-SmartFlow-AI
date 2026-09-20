"""
ML Preprocessing & Data Generation for SmartFlow AI.
Generates realistic historical traffic training datasets and builds reproducible feature pipelines.
"""
import os
from pathlib import Path
from typing import Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SAMPLE_DATA_PATH = DATA_DIR / "sample_traffic_data.csv"

FEATURE_COLS = [
    "hour",
    "day_of_week",
    "is_weekend",
    "road_type",
    "weather",
    "temperature",
    "precipitation",
    "vehicle_count",
    "free_flow_speed",
]

TARGET_COL = "congestion_level"  # 'LOW', 'MEDIUM', 'HIGH'


def generate_synthetic_traffic_dataset(
    output_path: Path = SAMPLE_DATA_PATH,
    n_samples: int = 5000,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Synthesize a rich, realistic historical traffic dataset with genuine physical correlations.
    Includes morning (8-10am) & evening (5-8pm) rush hours, weather degradation, and road capacities.
    """
    np.random.seed(random_seed)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    hours = np.random.randint(0, 24, size=n_samples)
    days = np.random.randint(0, 7, size=n_samples)  # 0=Mon, 6=Sun
    is_weekend = (days >= 5).astype(int)

    road_types = np.random.choice(["Highway", "Arterial", "Urban"], size=n_samples, p=[0.35, 0.40, 0.25])
    weather_types = np.random.choice(["Clear", "Rain", "Fog", "Storm"], size=n_samples, p=[0.70, 0.18, 0.08, 0.04])
    
    temps = np.random.normal(loc=28.0, scale=7.0, size=n_samples).clip(10, 48)
    
    precip = np.zeros(n_samples)
    for i in range(n_samples):
        if weather_types[i] == "Rain":
            precip[i] = np.random.exponential(scale=3.5)
        elif weather_types[i] == "Storm":
            precip[i] = np.random.exponential(scale=10.0) + 2.0
        elif weather_types[i] == "Fog":
            precip[i] = np.random.uniform(0.0, 0.5)

    # Free flow speed by road type
    free_flow = np.zeros(n_samples)
    base_capacity = np.zeros(n_samples)
    for i in range(n_samples):
        if road_types[i] == "Highway":
            free_flow[i] = np.random.normal(90.0, 5.0)
            base_capacity[i] = 1800
        elif road_types[i] == "Arterial":
            free_flow[i] = np.random.normal(60.0, 4.0)
            base_capacity[i] = 1200
        else:  # Urban
            free_flow[i] = np.random.normal(40.0, 3.0)
            base_capacity[i] = 800

    # Realistic vehicle count computation based on hour & weekend
    vehicle_counts = np.zeros(n_samples, dtype=int)
    avg_speeds = np.zeros(n_samples)
    congestion_levels = []
    delays_min = np.zeros(n_samples)
    risk_scores = np.zeros(n_samples, dtype=int)

    for i in range(n_samples):
        h = hours[i]
        wknd = is_weekend[i]
        cap = base_capacity[i]

        # Hour congestion factor
        if not wknd:
            if 8 <= h <= 10:
                h_factor = np.random.uniform(0.85, 1.35)  # Morning rush
            elif 17 <= h <= 20:
                h_factor = np.random.uniform(0.90, 1.40)  # Evening rush
            elif 11 <= h <= 16:
                h_factor = np.random.uniform(0.50, 0.85)  # Midday
            else:
                h_factor = np.random.uniform(0.15, 0.40)  # Night
        else:
            if 12 <= h <= 19:
                h_factor = np.random.uniform(0.60, 0.95)  # Weekend afternoon
            else:
                h_factor = np.random.uniform(0.15, 0.45)

        # Weather impediment
        w_factor = 1.0
        if weather_types[i] == "Rain":
            w_factor = 0.88
        elif weather_types[i] == "Fog":
            w_factor = 0.78
        elif weather_types[i] == "Storm":
            w_factor = 0.65

        # Computed vehicle volume
        v_count = int(np.clip(cap * h_factor * np.random.normal(1.0, 0.12), 40, cap * 1.5))
        vehicle_counts[i] = v_count

        # Greenshields traffic density speed model
        density_ratio = min(1.3, v_count / cap)
        speed = free_flow[i] * max(0.15, (1.0 - (0.75 * (density_ratio ** 1.8)))) * w_factor
        speed = max(8.0, min(free_flow[i], speed + np.random.normal(0, 2.0)))
        avg_speeds[i] = round(speed, 1)

        # Speed reduction ratio
        speed_deficit = 1.0 - (speed / free_flow[i])

        # True congestion classification
        if speed_deficit < 0.25 and density_ratio < 0.65:
            level = "LOW"
            score = int(np.random.uniform(8, 38))
            delay = round(max(0.0, np.random.normal(1.0, 0.8)), 1)
        elif speed_deficit < 0.50 and density_ratio < 0.95:
            level = "MEDIUM"
            score = int(np.random.uniform(40, 68))
            delay = round(np.random.uniform(4.0, 10.0), 1)
        else:
            level = "HIGH"
            score = int(np.random.uniform(70, 98))
            delay = round(np.random.uniform(12.0, 35.0), 1)

        congestion_levels.append(level)
        delays_min[i] = delay
        risk_scores[i] = score

    df = pd.DataFrame({
        "hour": hours,
        "day_of_week": days,
        "is_weekend": is_weekend,
        "road_type": road_types,
        "weather": weather_types,
        "temperature": np.round(temps, 1),
        "precipitation": np.round(precip, 2),
        "vehicle_count": vehicle_counts,
        "free_flow_speed": np.round(free_flow, 1),
        "avg_speed": avg_speeds,
        "delay_min": delays_min,
        "risk_score": risk_scores,
        "congestion_level": congestion_levels,
    })

    df.to_csv(output_path, index=False)
    return df


def load_or_generate_dataset(data_path: Path = SAMPLE_DATA_PATH) -> pd.DataFrame:
    """Load existing dataset or generate if not present."""
    if data_path.exists():
        return pd.read_csv(data_path)
    return generate_synthetic_traffic_dataset(output_path=data_path)


def build_preprocessor() -> ColumnTransformer:
    """Construct ColumnTransformer for numerical scaling and categorical encoding."""
    numeric_features = ["hour", "day_of_week", "is_weekend", "temperature", "precipitation", "vehicle_count", "free_flow_speed"]
    categorical_features = ["road_type", "weather"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
        ],
        remainder="drop",
    )
    return preprocessor


def prepare_train_test_data(
    df: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, ColumnTransformer, list]:
    """Preprocess data and split into train and test sets."""
    X = df[FEATURE_COLS]
    y = np.array(df[TARGET_COL].tolist(), dtype=object)

    preprocessor = build_preprocessor()
    X_transformed = preprocessor.fit_transform(X)

    # Get feature names after transformation
    cat_encoder = preprocessor.named_transformers_["cat"]
    cat_cols = cat_encoder.get_feature_names_out(["road_type", "weather"]).tolist()
    num_cols = ["hour", "day_of_week", "is_weekend", "temperature", "precipitation", "vehicle_count", "free_flow_speed"]
    all_feature_names = num_cols + cat_cols

    X_train, X_test, y_train, y_test = train_test_split(
        X_transformed, y, test_size=test_size, random_state=random_state, stratify=y
    )
    return X_train, X_test, y_train, y_test, preprocessor, all_feature_names
