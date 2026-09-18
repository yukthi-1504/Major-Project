# Script to load the trained model and make traffic predictions (pandas removed)
from pathlib import Path
try:
    import joblib
    _joblib_load = lambda p: joblib.load(p)
except Exception:
    import pickle
    _joblib_load = lambda p: pickle.load(open(p, 'rb'))
from datetime import datetime

# --- STEP 1: Paths ---
BASE_DIR = Path(__file__).resolve().parent  # ML/ folder
MODEL_PATH = BASE_DIR / "traffic_predictor.pkl"

# --- STEP 2: Load model ---
model = _joblib_load(MODEL_PATH)
print(f"Loaded model from {MODEL_PATH}")


def predict_next_hour(current_time, last_traffic):
    """Predict traffic for the next hour without pandas.

    NOTE: no campaign/discount — the current model is trained on real Olist
    order data, which has no promo signal, so those features were dropped
    everywhere (train_model.py, api/app.py too).
    """
    hour = current_time.hour
    day_of_week = current_time.weekday()

    # Lag features (use last traffic for all lags if no history)
    lag_1 = last_traffic
    lag_2 = last_traffic
    lag_3 = last_traffic

    # Rolling mean and std (approximate using last_traffic)
    rolling_mean_3 = last_traffic
    rolling_std_3 = 0.0

    # One-hot encode day_of_week
    day_features = [0] * 7
    day_features[day_of_week] = 1

    # Prepare feature vector as numpy array
    feature_values = [hour, last_traffic,
                      lag_1, lag_2, lag_3, rolling_mean_3, rolling_std_3] + day_features

    import pandas as pd
    # Column names must match model.feature_names_in_ from training
    feature_names = ['hour', 'past_traffic',
                     'lag_1', 'lag_2', 'lag_3', 'rolling_mean_3', 'rolling_std_3'] + \
                     [f'day_{i}' for i in range(7)]
    input_df = pd.DataFrame([feature_values], columns=feature_names)

    predicted_traffic = model.predict(input_df)[0]
    return predicted_traffic


def scale_replicas(predicted_traffic):
    """Simple rule-based scaling.

    Thresholds tuned for real Olist-scale traffic (mean ~7/hr, max ~104/hr in
    the dense 2017-2018 window) — much lower than the old synthetic-data
    thresholds (up to 300+/hr).
    """
    if predicted_traffic <= 10:
        return 1
    elif predicted_traffic <= 25:
        return 2
    elif predicted_traffic <= 50:
        return 3
    elif predicted_traffic <= 80:
        return 4
    else:
        return 5
if __name__ == "__main__":
    print("Starting prediction script...")
    current_time = datetime.now()
    last_traffic = 20

    predicted = predict_next_hour(current_time, last_traffic)
    replicas = scale_replicas(predicted)

    print(f"Predicted traffic for next hour: {predicted:.0f}")
    print(f"Recommended K8s replicas: {replicas}")
