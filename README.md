# crop_recommendation_system
Intro to Ai Final Group Project

## API + USSD service

The Random Forest model is served via a small Flask API in `api/`, which also
powers a USSD front end so the recommender can be used from a basic feature
phone (no internet/smartphone required).

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Train and save the model artifacts

```bash
python api/train_model.py
```

This reproduces `notebooks/Random_forest_model.ipynb` and writes the fitted
model, label encoder, and feature column order to `model_artifacts/`.

### 3. Run the API

```bash
cd api
python app.py
```

Runs on `http://localhost:5001`.

### 4. Endpoints

- `GET /health` — liveness check.
- `POST /predict` — general-purpose JSON endpoint for any client (web app, mobile app, etc.):

  ```bash
  curl -X POST http://localhost:5001/predict \
    -H "Content-Type: application/json" \
    -d '{"N":90,"P":42,"K":43,"temperature":20.9,"humidity":82,"ph":6.5,"rainfall":203}'
  ```

  Returns the predicted crop plus the top-3 class probabilities.

- `POST /ussd` — USSD gateway webhook, following the Africa's Talking `CON`/`END`
  text protocol (form-encoded `sessionId`, `phoneNumber`, `serviceCode`, `text`).
  It walks the caller through entering N, P, K, temperature, humidity, pH, and
  rainfall one screen at a time, then ends the session with the recommended crop.

### 5. Testing the USSD flow

Since a real telco short code requires a carrier agreement, prototype with
[Africa's Talking](https://africastalking.com)'s free sandbox and built-in USSD
simulator:

1. Expose your local server publicly, e.g. `ngrok http 5001`.
2. In the Africa's Talking sandbox, create a USSD channel and set the callback
   URL to `https://<your-ngrok-subdomain>.ngrok.io/ussd`.
3. Use the sandbox's USSD simulator (or dial the sandbox shortcode from the
   simulator) to walk through the flow end to end.

You can also simulate it locally with `curl`, growing the `text` field one
answer at a time to mimic successive key-presses:

```bash
curl -X POST http://localhost:5001/ussd -d "sessionId=1&phoneNumber=+233000000000&serviceCode=*123#&text="
curl -X POST http://localhost:5001/ussd -d "sessionId=1&phoneNumber=+233000000000&serviceCode=*123#&text=90"
curl -X POST http://localhost:5001/ussd -d "sessionId=1&phoneNumber=+233000000000&serviceCode=*123#&text=90*42*43*20.9*82*6.5*203"
```

The last call should return `END Recommended crop: rice`.
