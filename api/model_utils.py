"""
Loads the trained Random Forest model artifacts once and exposes a single
predict_crop() function that both /predict and /ussd route through.
"""

import json
from pathlib import Path

import joblib

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "model_artifacts"

_model = joblib.load(ARTIFACTS_DIR / "random_forest_model.joblib")
_label_encoder = joblib.load(ARTIFACTS_DIR / "label_encoder.joblib")
with open(ARTIFACTS_DIR / "feature_columns.json") as f:
    FEATURE_COLUMNS = json.load(f)

TOP_K = 3


def predict_crop(features: dict) -> dict:
    """
    features: dict with keys matching FEATURE_COLUMNS, numeric values.
    Returns {"crop": str, "top_predictions": [{"crop": str, "probability": float}, ...]}
    """
    ordered_values = [[features[col] for col in FEATURE_COLUMNS]]

    predicted_index = _model.predict(ordered_values)[0]
    crop = _label_encoder.inverse_transform([predicted_index])[0]

    probabilities = _model.predict_proba(ordered_values)[0]
    ranked = sorted(
        zip(_label_encoder.classes_, probabilities), key=lambda pair: pair[1], reverse=True
    )[:TOP_K]

    return {
        "crop": crop,
        "top_predictions": [
            {"crop": name, "probability": round(float(prob), 4)} for name, prob in ranked
        ],
    }
