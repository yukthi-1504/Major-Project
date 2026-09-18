# train_model.py
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

# --- STEP 1: Setup paths ---
BASE_DIR = Path(__file__).resolve().parent  # ML/ folder

# Pick which dataset to train on: "olist" (real orders) or "synthetic" (fake demo data).
# Override without editing this file: DATASET=synthetic python ml/train_model.py
DATASETS = {
    "olist": "olist_hourly_traffic.csv",
    "synthetic": "synthetic_flashsale_data.csv",
}
DATASET_CHOICE = os.environ.get("DATASET", "olist")
DATA_PATH = BASE_DIR.parent / "data" / "raw" / DATASETS[DATASET_CHOICE]
# The API serves both models side by side (real-data default + synthetic
# campaign-aware demo), so each dataset needs its own model file.
MODEL_FILENAMES = {
    "olist": "traffic_predictor.pkl",
    "synthetic": "traffic_predictor_synthetic.pkl",
}
MODEL_PATH = BASE_DIR / MODEL_FILENAMES[DATASET_CHOICE]

# Figures are always saved to disk (per-dataset folder) so they exist
# regardless of terminal/backend quirks with interactive plt.show() windows.
PLOTS_DIR = BASE_DIR.parent / "reports" / "figures" / DATASET_CHOICE
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def save_and_show(filename):
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / filename, dpi=150)
    print(f"Saved plot: {PLOTS_DIR / filename}")
    try:
        plt.show()
    except Exception:
        pass  # no interactive display available; the saved PNG is enough


print(f"Loading dataset from: {DATA_PATH}")

# --- STEP 2: Load Dataset ---
df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])

# --- OPTIONAL: Clean up data types for display ---
# Convert 'past_traffic' to integer (rounding first just in case)
if 'past_traffic' in df.columns:
    df['past_traffic'] = df['past_traffic'].round().astype(int)

print("Dataset loaded successfully!")
print(df.head())

# --- STEP 3: Basic EDA ---
plt.figure(figsize=(12,5))
plt.plot(df['timestamp'], df['traffic'], label='Traffic')
plt.title('Traffic over Time')
plt.xlabel('Timestamp')
plt.ylabel('Traffic')
plt.legend()
save_and_show('traffic_over_time.png')


plt.figure(figsize=(8,4))
sns.boxplot(x='hour', y='traffic', data=df)
plt.title('Traffic vs Hour of Day')
save_and_show('traffic_vs_hour.png')

# campaign only exists in the synthetic dataset — Olist has no real promo
# signal, and we deliberately chose not to fabricate one for real data.
if 'campaign' in df.columns:
    plt.figure(figsize=(6,4))
    sns.boxplot(x='campaign', y='traffic', data=df)
    plt.title('Traffic vs Campaign')
    save_and_show('traffic_vs_campaign.png')


# --- STEP 4: Feature Engineering ---
# Lag features: traffic of previous 1,2,3 hours
df['lag_1'] = df['traffic'].shift(1).fillna(df['traffic'].mean())
df['lag_2'] = df['traffic'].shift(2).fillna(df['traffic'].mean())
df['lag_3'] = df['traffic'].shift(3).fillna(df['traffic'].mean())

# Rolling mean & std of past 3 hours
df['rolling_mean_3'] = df['traffic'].rolling(3, min_periods=1).mean()
df['rolling_std_3'] = df['traffic'].rolling(3, min_periods=1).std().fillna(0)

# One-hot encode day_of_week
df = pd.get_dummies(df, columns=['day_of_week'], prefix='day')

# --- STEP 5: Prepare Features & Target ---
# campaign/discount only exist in the synthetic dataset (real Olist orders have
# no promo signal) - include them when present so the synthetic model can
# actually learn the campaign effect, instead of silently ignoring it.
FEATURES = ['hour', 'past_traffic',
            'lag_1', 'lag_2', 'lag_3', 'rolling_mean_3', 'rolling_std_3'] + \
           [col for col in ('campaign', 'discount') if col in df.columns] + \
           [col for col in df.columns if col.startswith('day_')]

TARGET = 'traffic'

X = df[FEATURES]
y = df[TARGET]

# Time-based split, NOT random: data is already sorted by timestamp, so the
# last 20% of hours (chronologically) become the test set. A random split
# would leak future hours into training (e.g. train on 3pm, test on 2pm the
# same day) and make the model look better than it actually is at forecasting.
split_idx = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

# --- STEP 6: Train Random Forest Regressor ---
model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# --- STEP 7: Evaluate Model ---
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"Model Evaluation → MAE: {mae:.2f}, RMSE: {rmse:.2f}")
# Optional: Plot true vs predicted
plt.figure(figsize=(8,4))
plt.scatter(y_test, y_pred, alpha=0.6)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
plt.xlabel('True Traffic')
plt.ylabel('Predicted Traffic')
plt.title('True vs Predicted Traffic')
save_and_show('true_vs_predicted.png')


# --- STEP 8: Save Model ---
# --- STEP 8: Save Model ---
joblib.dump(model, MODEL_PATH)
print(f"Model saved as {MODEL_PATH}")

# --- STEP 9: Detailed Metrics & Feature Importance ---
print("\n" + "="*40)
print("     DETAILED MODEL REPORT")
print("="*40)

# 1. Feature Importance
importances = model.feature_importances_
feature_importance_df = pd.DataFrame({'Feature': FEATURES, 'Importance': importances})
feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)
print("\nFeature Importance Percentage:")
for index, row in feature_importance_df.iterrows():
    print(f"{row['Feature']}: {row['Importance']*100:.0f}%")

plt.figure(figsize=(8, 5))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'] * 100)
plt.xlabel('Importance (%)')
plt.title(f'Feature Importance — {DATASET_CHOICE} dataset')
plt.gca().invert_yaxis()  # most important feature on top
save_and_show('feature_importance.png')

# 2. Number of Iterations (Trees)
print(f"\nNumber of Iterations (Trees): {model.n_estimators}")

# 3. Improvement Percentage vs Baseline
# Baseline: Always predict the average traffic of the training set
baseline_pred = np.full(len(y_test), y_train.mean())
baseline_mae = mean_absolute_error(y_test, baseline_pred)
baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_pred))

mae_improvement = ((baseline_mae - mae) / baseline_mae) * 100
rmse_improvement = ((baseline_rmse - rmse) / baseline_rmse) * 100

print(f"\nBaseline MAE (Mean Predictor): {baseline_mae:.0f}")
print(f"Model MAE: {mae:.0f}")
print(f"Improvement Percentage (MAE): {mae_improvement:.0f}%")

print(f"\nBaseline RMSE (Mean Predictor): {baseline_rmse:.0f}")
print(f"Model RMSE: {rmse:.0f}")
print(f"Improvement Percentage (RMSE): {rmse_improvement:.0f}%")
print("="*40 + "\n")
