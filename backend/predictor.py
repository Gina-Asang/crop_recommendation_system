from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap


# FEATURES USED BY THE RANDOM FOREST


FEATURES = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall"
]


FEATURE_NAMES = {
    "N": "Nitrogen",
    "P": "Phosphorus",
    "K": "Potassium",
    "temperature": "Temperature",
    "humidity": "Humidity",
    "ph": "Soil pH",
    "rainfall": "Rainfall"
}


# LOAD THE TRAINED RANDOM FOREST


MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "model"
    / "random_forest_model.pkl"
)

model = joblib.load(MODEL_PATH)


# CREATE THE SHAP EXPLAINER


# TreeExplainer is made for tree-based models such as
# Random Forest. It explains one particular prediction
# by showing how each input contributed to that output.
explainer = shap.TreeExplainer(model)



# FORMAT INPUT VALUES FOR THE USER


def format_value(feature, value):
    value = float(value)

    if feature in ["N", "P", "K"]:
        return f"{value:.0f}"

    if feature == "temperature":
        return f"{value:.2f} °C"

    if feature == "humidity":
        return f"{value:.2f}%"

    if feature == "ph":
        return f"{value:.2f}"

    if feature == "rainfall":
        return f"{value:.2f} mm"

    return f"{value:.2f}"



# GET SHAP VALUES FOR THE PREDICTED CROP


def get_predicted_class_shap_values(input_data, predicted_crop):
    shap_values = explainer.shap_values(input_data)

    classes = list(model.classes_)
    class_index = classes.index(predicted_crop)

    # Older SHAP versions may return one array per class.
    if isinstance(shap_values, list):
        selected = np.asarray(shap_values[class_index])
        return selected[0]

    shap_array = np.asarray(shap_values)

    # SHAP 0.50 commonly returns:
    # samples x features x classes
    if (
        shap_array.ndim == 3
        and shap_array.shape[0] == 1
        and shap_array.shape[1] == len(FEATURES)
        and shap_array.shape[2] == len(classes)
    ):
        return shap_array[0, :, class_index]

    # Alternative layout:
    # samples x classes x features
    if (
        shap_array.ndim == 3
        and shap_array.shape[0] == 1
        and shap_array.shape[1] == len(classes)
        and shap_array.shape[2] == len(FEATURES)
    ):
        return shap_array[0, class_index, :]

    # Alternative layout:
    # classes x samples x features
    if (
        shap_array.ndim == 3
        and shap_array.shape[0] == len(classes)
        and shap_array.shape[1] == 1
        and shap_array.shape[2] == len(FEATURES)
    ):
        return shap_array[class_index, 0, :]

    raise ValueError(
        f"Unexpected SHAP output shape: {shap_array.shape}"
    )



# EXPLAIN THIS PARTICULAR MODEL PREDICTION


def explain_prediction(input_data, values, predicted_crop):
    shap_values = get_predicted_class_shap_values(
        input_data,
        predicted_crop
    )

    contributions = []

    for index, feature in enumerate(FEATURES):
        contributions.append({
            "feature": feature,
            "display_name": FEATURE_NAMES[feature],
            "value": float(values[feature]),
            "shap_value": float(shap_values[index])
        })

    # We want to explain which inputs pushed the model
    # TOWARD the crop that it predicted.
    positive = [
        item
        for item in contributions
        if item["shap_value"] > 0
    ]

    positive.sort(
        key=lambda item: item["shap_value"],
        reverse=True
    )

    # Usually there will be at least three positive
    # contributors. If not, use the largest remaining
    # contributions so the explanation still works.
    strongest = positive[:3]

    if len(strongest) < 3:
        remaining = [
            item
            for item in contributions
            if item not in strongest
        ]

        remaining.sort(
            key=lambda item: item["shap_value"],
            reverse=True
        )

        strongest.extend(
            remaining[:3 - len(strongest)]
        )

    # The bars in the interface are relative to the
    # strongest displayed contributor. They are for
    # easy visual comparison, not probabilities.
    max_positive = max(
        [max(item["shap_value"], 0) for item in strongest] + [1e-9]
    )

    rank_labels = [
        "Strongest contributor",
        "Second strongest contributor",
        "Third strongest contributor"
    ]

    explanation = []

    for index, item in enumerate(strongest):
        contribution = item["shap_value"]

        relative_strength = (
            max(contribution, 0) / max_positive
        ) * 100

        value_text = format_value(
            item["feature"],
            item["value"]
        )

        if contribution > 0:
            if index == 0:
                sentence = (
                    f"Your {item['display_name'].lower()} value "
                    f"of {value_text} had the largest positive "
                    f"influence on the model's {predicted_crop} prediction."
                )
            else:
                sentence = (
                    f"Your {item['display_name'].lower()} value "
                    f"of {value_text} also pushed the model "
                    f"toward predicting {predicted_crop}."
                )
        else:
            sentence = (
                f"Your {item['display_name'].lower()} value "
                f"of {value_text} was among the most influential "
                f"inputs considered for this prediction."
            )

        explanation.append({
            "feature": item["display_name"],
            "value": value_text,
            "rank_label": rank_labels[index],
            "relative_strength": round(relative_strength, 1),
            "text": sentence
        })

    return explanation



# MAIN PREDICTION FUNCTION USED BY FLASK


def predict_crop(values):
    input_data = pd.DataFrame(
        [[
            values["N"],
            values["P"],
            values["K"],
            values["temperature"],
            values["humidity"],
            values["ph"],
            values["rainfall"]
        ]],
        columns=FEATURES
    )

    # Main crop prediction from the trained Random Forest.
    predicted_crop = str(model.predict(input_data)[0])

    # Model probabilities for all 22 crop classes.
    probabilities = model.predict_proba(input_data)[0]

    ranked = sorted(
        zip(model.classes_, probabilities),
        key=lambda item: item[1],
        reverse=True
    )

    # Keep the top three model outputs.
    top_predictions = []

    for crop, probability in ranked[:3]:
        top_predictions.append({
            "crop": str(crop),
            "probability": round(float(probability) * 100, 1)
        })

    # Explain the exact Random Forest prediction using SHAP.
    model_explanation = explain_prediction(
        input_data,
        values,
        predicted_crop
    )

    return {
        "recommended_crop": predicted_crop,
        "model_explanation": model_explanation,
        "top_predictions": top_predictions
    }