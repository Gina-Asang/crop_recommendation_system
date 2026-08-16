"""
Trains the Random Forest crop recommendation model and saves it, along with
the label encoder and feature column order, to model_artifacts/ so the Flask
API (api/app.py) can load them without retraining.

Mirrors notebooks/Random_forest_model.ipynb (same features, same
RandomForestClassifier hyperparameters), but fits on the full dataset since
this is producing the final serving artifact rather than an experiment.
"""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

REPO_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = REPO_ROOT / "Dataset" / "Crop_recommendation_dataset.csv"
ARTIFACTS_DIR = REPO_ROOT / "model_artifacts"

FEATURE_COLUMNS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
RANDOM_STATE = 42


def main():
    df = pd.read_csv(DATASET_PATH)

    X = df[FEATURE_COLUMNS]
    le = LabelEncoder()
    y = le.fit_transform(df["label"])

    # Held-out split purely to report a sanity-check accuracy number;
    # the artifact we ship is refit on all the data below.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    sanity_model = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)
    sanity_model.fit(X_train, y_train)
    test_accuracy = accuracy_score(y_test, sanity_model.predict(X_test))
    print(f"Held-out test accuracy: {test_accuracy:.4f}")

    # Final artifact: refit on the full dataset to use all available signal.
    final_model = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)
    final_model.fit(X, y)

    ARTIFACTS_DIR.mkdir(exist_ok=True)
    joblib.dump(final_model, ARTIFACTS_DIR / "random_forest_model.joblib")
    joblib.dump(le, ARTIFACTS_DIR / "label_encoder.joblib")
    with open(ARTIFACTS_DIR / "feature_columns.json", "w") as f:
        json.dump(FEATURE_COLUMNS, f, indent=2)

    print(f"Saved model, label encoder, and feature columns to {ARTIFACTS_DIR}")


if __name__ == "__main__":
    main()
