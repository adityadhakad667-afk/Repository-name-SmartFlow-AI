"""
ML Package for SmartFlow AI.
Exports training, preprocessing, model container, and prediction routines.
"""
from .model import TrafficModel
from .predict import predict_traffic_conditions, get_model_instance
from .preprocessing import load_or_generate_dataset, FEATURE_COLS
from .train import train_models

__all__ = [
    "TrafficModel",
    "predict_traffic_conditions",
    "get_model_instance",
    "load_or_generate_dataset",
    "FEATURE_COLS",
    "train_models",
]
