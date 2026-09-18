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


# --- Load Model ---
BASE_DIR = Path(__file__).resolve().parent.parent / "ml"
MODEL_PATH = BASE_DIR / "traffic_predictor.pkl"

try:
    model = joblib.load(MODEL_PATH)
    print(f"Model loaded from {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "API is running", "model_loaded": model is not None})

@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        data = request.get_json()
        
        # Parse input
        current_time = datetime.strptime(data['current_time'], "%Y-%m-%d %H:%M:%S")
        hour = current_time.hour
        day_of_week = current_time.weekday()
        
        # Create features. NOTE: no campaign/discount — the current model is
        # trained on real Olist order data, which has no promo signal, so
        # those two features were dropped everywhere (train_model.py too).
        features = {
            'hour': hour,
            'past_traffic': data.get('last_traffic', 0),
            'lag_1': data.get('last_traffic', 0), # Simplified for single prediction
            'lag_2': data.get('last_traffic', 0),
            'lag_3': data.get('last_traffic', 0),
            'rolling_mean_3': data.get('last_traffic', 0),
            'rolling_std_3': 0,
        }

        # Add day features
        for i in range(7):
            features[f'day_{i}'] = 1 if i == day_of_week else 0

        # Create DataFrame ensuring correct column order (must match
        # model.feature_names_in_ from training)
        feature_list = ['hour', 'past_traffic',
                       'lag_1', 'lag_2', 'lag_3', 'rolling_mean_3', 'rolling_std_3'] + \
                       [f'day_{i}' for i in range(7)]
                       
        input_df = pd.DataFrame([features])[feature_list]
        
        # Predict
        prediction = model.predict(input_df)[0]
        
        # Scale replicas logic. Thresholds tuned for real Olist-scale traffic
        # (mean ~7/hr, max ~104/hr in the dense 2017-2018 window) — much
        # lower than the old synthetic-data thresholds (up to 300+/hr).
        replicas = 1
        if prediction > 80: replicas = 5
        elif prediction > 50: replicas = 4
        elif prediction > 25: replicas = 3
        elif prediction > 10: replicas = 2
        
        return jsonify({
            "predicted_traffic": int(round(prediction)),
            "recommended_replicas": replicas,
            "status": "success"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
