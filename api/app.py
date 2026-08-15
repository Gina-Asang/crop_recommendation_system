"""
Flask API serving the Random Forest crop recommendation model.

Endpoints:
  GET  /health   - liveness check
  POST /predict  - JSON in/out, for web/mobile clients
  POST /ussd     - Africa's Talking-style USSD webhook (CON/END text protocol)
"""

from flask import Flask, jsonify, request

from model_utils import FEATURE_COLUMNS, predict_crop
from simulator_page import SIMULATOR_HTML

app = Flask(__name__)

# (feature name, prompt shown to the USSD user) in the order they're collected
USSD_QUESTIONS = [
    ("N", "Enter Nitrogen (N) level in soil (kg/ha):"),
    ("P", "Enter Phosphorus (P) level in soil (kg/ha):"),
    ("K", "Enter Potassium (K) level in soil (kg/ha):"),
    ("temperature", "Enter temperature (deg C):"),
    ("humidity", "Enter relative humidity (%):"),
    ("ph", "Enter soil pH (0-14):"),
    ("rainfall", "Enter rainfall (mm):"),
]
assert [name for name, _ in USSD_QUESTIONS] == FEATURE_COLUMNS


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/simulator")
def simulator():
    """Phone-style web UI that calls /ussd like a real USSD gateway would."""
    return SIMULATOR_HTML


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True) or {}

    missing = [col for col in FEATURE_COLUMNS if col not in payload]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    features = {}
    for col in FEATURE_COLUMNS:
        try:
            features[col] = float(payload[col])
        except (TypeError, ValueError):
            return jsonify({"error": f"Field '{col}' must be a number"}), 400

    return jsonify(predict_crop(features))


@app.post("/ussd")
def ussd():
    """
    Africa's Talking webhook contract: form-encoded sessionId, phoneNumber,
    serviceCode, text. `text` is every answer entered so far, joined by '*'.
    Reply text must be prefixed CON (continue session) or END (close session).

    Stateless by design: re-derive progress from `text` on every request
    instead of keeping session state server-side. Progress is measured by
    how many *valid* numbers have been entered so far, so a bad entry just
    gets re-prompted without breaking the count of remaining questions.
    """
    text = request.values.get("text", "")
    raw_inputs = text.split("*") if text else []

    valid_values = []
    for raw in raw_inputs:
        try:
            valid_values.append(float(raw))
        except ValueError:
            pass

    last_input_invalid = bool(raw_inputs) and len(valid_values) < len(raw_inputs)

    if len(valid_values) >= len(USSD_QUESTIONS):
        features = dict(zip(FEATURE_COLUMNS, valid_values[: len(USSD_QUESTIONS)]))
        result = predict_crop(features)
        response = f"END Recommended crop: {result['crop']}"
    else:
        _, prompt = USSD_QUESTIONS[len(valid_values)]
        prefix = "Invalid input, please enter a number.\n" if last_input_invalid else ""
        response = f"CON {prefix}{prompt}"

    return response, 200, {"Content-Type": "text/plain"}


if __name__ == "__main__":
   
    app.run(debug=True, port=5001)
