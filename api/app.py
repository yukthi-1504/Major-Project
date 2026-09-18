from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow requests from file:// and any other origin

# Suppress development server warning
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# --- Load Models ---
# Two models, side by side: "real" is the production default, trained on
# actual Olist e-commerce orders (no promo signal in that data). "synthetic"
# is trained on simulated data that includes a campaign/discount effect, kept
# specifically to demonstrate what campaign-aware scaling looks like — real
# order data has no such field, so this can't be shown on the real model.
BASE_DIR = Path(__file__).resolve().parent.parent / "ml"
MODEL_PATHS = {
    "real": BASE_DIR / "traffic_predictor.pkl",
    "synthetic": BASE_DIR / "traffic_predictor_synthetic.pkl",
}

models = {}
for mode, path in MODEL_PATHS.items():
    try:
        models[mode] = joblib.load(path)
        print(f"Model '{mode}' loaded from {path}")
    except Exception as e:
        print(f"Error loading model '{mode}': {e}")
        models[mode] = None

# Scaling thresholds differ per model because the two datasets operate at
# very different traffic scales (real Olist: mean ~7/hr, peak ~104/hr;
# synthetic: designed to range 30-300+/hr).
REPLICA_THRESHOLDS = {
    "real":      [(80, 5), (50, 4), (25, 3), (10, 2)],
    "synthetic": [(300, 5), (200, 4), (100, 3), (50, 2)],
}


def replicas_for(prediction, mode):
    for threshold, replicas in REPLICA_THRESHOLDS[mode]:
        if prediction > threshold:
            return replicas
    return 1


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "API is running",
        "model_loaded": models["real"] is not None,
        "models": {mode: m is not None for mode, m in models.items()},
    })

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    mode = data.get('mode', 'real')

    if mode not in models:
        return jsonify({"error": f"Unknown mode '{mode}', expected 'real' or 'synthetic'"}), 400

    model = models[mode]
    if not model:
        return jsonify({"error": f"Model '{mode}' not loaded"}), 500

    try:
        # Parse input
        current_time = datetime.strptime(data['current_time'], "%Y-%m-%d %H:%M:%S")
        hour = current_time.hour
        day_of_week = current_time.weekday()

        features = {
            'hour': hour,
            'past_traffic': data.get('last_traffic', 0),
            'lag_1': data.get('last_traffic', 0), # Simplified for single prediction
            'lag_2': data.get('last_traffic', 0),
            'lag_3': data.get('last_traffic', 0),
            'rolling_mean_3': data.get('last_traffic', 0),
            'rolling_std_3': 0,
        }

        feature_list = ['hour', 'past_traffic',
                       'lag_1', 'lag_2', 'lag_3', 'rolling_mean_3', 'rolling_std_3']

        # campaign/discount only exist (and were only trained on) the
        # synthetic model — real Olist orders have no promo signal.
        if mode == 'synthetic':
            features['campaign'] = data.get('campaign', 0)
            features['discount'] = data.get('discount', 0)
            feature_list += ['campaign', 'discount']

        # Add day features
        for i in range(7):
            features[f'day_{i}'] = 1 if i == day_of_week else 0
        feature_list += [f'day_{i}' for i in range(7)]

        # Create DataFrame ensuring correct column order (must match
        # model.feature_names_in_ from training)
        input_df = pd.DataFrame([features])[feature_list]

        # Predict
        prediction = model.predict(input_df)[0]
        replicas = replicas_for(prediction, mode)

        return jsonify({
            "predicted_traffic": int(round(prediction)),
            "recommended_replicas": replicas,
            "model": mode,
            "status": "success"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
