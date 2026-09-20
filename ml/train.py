"""
Model Training & Evaluation Pipeline for SmartFlow AI.
Trains and compares RandomForestClassifier and XGBClassifier on traffic datasets.
Evaluates metrics (Accuracy, Precision, Recall, F1, Confusion Matrix) and persists best model.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from xgboost import XGBClassifier

from .preprocessing import (
    load_or_generate_dataset,
    prepare_train_test_data,
    SAMPLE_DATA_PATH,
)

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_FILE = MODELS_DIR / "traffic_classifier.joblib"
METADATA_FILE = MODELS_DIR / "model_metadata.json"

CLASSES = ["LOW", "MEDIUM", "HIGH"]
CLASS_TO_INT = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}


def train_models(
    data_path: Path = SAMPLE_DATA_PATH,
    model_output_path: Path = MODEL_FILE,
    metadata_output_path: Path = METADATA_FILE,
) -> Dict[str, Any]:
    """Train Random Forest and XGBoost models, evaluate and save best model."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_or_generate_dataset(data_path)

    X_train, X_test, y_train_str, y_test_str, preprocessor, feature_names = prepare_train_test_data(df)

    y_train_int = np.array([CLASS_TO_INT[s] for s in y_train_str])
    y_test_int = np.array([CLASS_TO_INT[s] for s in y_test_str])

    # 1. Random Forest Classifier
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train_str)
    y_pred_rf_str = rf.predict(X_test)
    y_pred_rf = np.array([CLASS_TO_INT[s] for s in y_pred_rf_str])

    rf_acc = accuracy_score(y_test_str, y_pred_rf_str)
    rf_prec, rf_rec, rf_f1, _ = precision_recall_fscore_support(y_test_str, y_pred_rf_str, average="weighted", zero_division=0)
    rf_cm = confusion_matrix(y_test_str, y_pred_rf_str, labels=CLASSES).tolist()

    # 2. XGBoost Classifier
    xgb = XGBClassifier(
        n_estimators=120,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        eval_metric="mlogloss",
    )
    xgb.fit(X_train, y_train_int)
    y_pred_xgb_int = xgb.predict(X_test)
    xgb_acc = accuracy_score(y_test_int, y_pred_xgb_int)
    xgb_prec, xgb_rec, xgb_f1, _ = precision_recall_fscore_support(y_test_int, y_pred_xgb_int, average="weighted", zero_division=0)
    xgb_cm = confusion_matrix(y_test_int, y_pred_xgb_int, labels=[0, 1, 2]).tolist()

    # Select best model based on F1 score
    if xgb_f1 >= rf_f1:
        best_name = "XGBoost Classifier"
        best_model = xgb
        best_acc, best_prec, best_rec, best_f1, best_cm = xgb_acc, xgb_prec, xgb_rec, xgb_f1, xgb_cm
        raw_importances = xgb.feature_importances_
    else:
        best_name = "Random Forest Classifier"
        best_model = rf
        best_acc, best_prec, best_rec, best_f1, best_cm = rf_acc, rf_prec, rf_rec, rf_f1, rf_cm
        raw_importances = rf.feature_importances_

    # Map raw transformed importances back to high-level features
    feature_importances = {}
    for fn, imp in zip(feature_names, raw_importances):
        # group categorical features back to base name
        base_name = fn.split("__")[-1] if "__" in fn else fn
        base_name = base_name.split("_")[0] if any(base_name.startswith(c) for c in ["road", "weather"]) else base_name
        feature_importances[base_name] = feature_importances.get(base_name, 0.0) + float(imp)

    # Normalize feature importances
    total_imp = sum(feature_importances.values()) or 1.0
    feature_importances = {k: round(v / total_imp, 4) for k, v in feature_importances.items()}

    # Package pipeline
    pipeline = {
        "preprocessor": preprocessor,
        "classifier": best_model,
        "feature_names": feature_names,
    }

    joblib.dump(pipeline, model_output_path)

    metadata = {
        "best_model_name": best_name,
        "accuracy": round(best_acc, 4),
        "precision": round(best_prec, 4),
        "recall": round(best_rec, 4),
        "f1_score": round(best_f1, 4),
        "confusion_matrix": best_cm,
        "classes": CLASSES,
        "feature_importances": feature_importances,
        "training_samples_count": len(df),
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "models_comparison": {
            "Random Forest": {
                "accuracy": round(rf_acc, 4),
                "precision": round(rf_prec, 4),
                "recall": round(rf_rec, 4),
                "f1_score": round(rf_f1, 4),
                "confusion_matrix": rf_cm,
            },
            "XGBoost": {
                "accuracy": round(xgb_acc, 4),
                "precision": round(xgb_prec, 4),
                "recall": round(xgb_rec, 4),
                "f1_score": round(xgb_f1, 4),
                "confusion_matrix": xgb_cm,
            },
        },
    }

    with open(metadata_output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Model training complete. Selected {best_name} with F1={best_f1:.4f}")
    return metadata


if __name__ == "__main__":
    train_models()
