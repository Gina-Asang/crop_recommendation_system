from flask import Flask, jsonify, render_template, request
from predictor import predict_crop

app = Flask(__name__)

# Exact observed limits in the project dataset. These limits are enforced in both
# the browser and the backend so out-of-range values are not accepted.
FIELDS = {
    "N": (0, 140, "Nitrogen"),
    "P": (5, 145, "Phosphorus"),
    "K": (5, 205, "Potassium"),
    "temperature": (8.826, 43.675, "Temperature"),
    "humidity": (14.258, 99.982, "Humidity"),
    "ph": (3.505, 9.935, "pH"),
    "rainfall": (20.211, 298.560, "Rainfall"),
}


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/predict")
def predict():
    data = request.get_json(silent=True) or {}
    values = {}

    for field, (minimum, maximum, display_name) in FIELDS.items():
        if field not in data:
            return jsonify({"error": f"Please enter {display_name}."}), 400

        try:
            value = float(data[field])
        except (TypeError, ValueError):
            return jsonify({"error": f"{display_name} must be a number."}), 400

        if not minimum <= value <= maximum:
            return jsonify({
                "error": f"{display_name} must be between {minimum:g} and {maximum:g}."
            }), 400

        values[field] = value

    result = predict_crop(values)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
