"""Train the same model on both datasets and plot true-vs-predicted side by side.

Shows the honest tradeoff discussed in the project writeup: synthetic data looks
cleaner/more dramatic, real (Olist) data is the trustworthy result.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE_DIR = Path(__file__).resolve().parent
DATASETS = {
    "olist": "olist_hourly_traffic.csv",
    "synthetic": "synthetic_flashsale_data.csv",
}
PLOTS_DIR = BASE_DIR.parent / "reports" / "figures" / "comparison"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def train_and_evaluate(dataset_key):
    data_path = BASE_DIR.parent / "data" / "raw" / DATASETS[dataset_key]
    df = pd.read_csv(data_path, parse_dates=["timestamp"])

    df['lag_1'] = df['traffic'].shift(1).fillna(df['traffic'].mean())
    df['lag_2'] = df['traffic'].shift(2).fillna(df['traffic'].mean())
    df['lag_3'] = df['traffic'].shift(3).fillna(df['traffic'].mean())
    df['rolling_mean_3'] = df['traffic'].rolling(3, min_periods=1).mean()
    df['rolling_std_3'] = df['traffic'].rolling(3, min_periods=1).std().fillna(0)
    df = pd.get_dummies(df, columns=['day_of_week'], prefix='day')

    features = ['hour', 'past_traffic', 'lag_1', 'lag_2', 'lag_3',
                'rolling_mean_3', 'rolling_std_3'] + \
        [col for col in df.columns if col.startswith('day_')]

    X, y = df[features], df['traffic']
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    return y_test, y_pred, mae, rmse


fig, axes = plt.subplots(1, 2, figsize=(13, 5))

for ax, dataset_key in zip(axes, ["olist", "synthetic"]):
    y_test, y_pred, mae, rmse = train_and_evaluate(dataset_key)
    ax.scatter(y_test, y_pred, alpha=0.5)
    ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
    ax.set_xlabel('True Traffic')
    ax.set_ylabel('Predicted Traffic')
    label = "Olist (real)" if dataset_key == "olist" else "Synthetic (fake)"
    ax.set_title(f'{label}\nMAE={mae:.2f}, RMSE={rmse:.2f}')
    print(f"{dataset_key}: MAE={mae:.2f}, RMSE={rmse:.2f}")

plt.tight_layout()
out_path = PLOTS_DIR / "real_vs_synthetic.png"
plt.savefig(out_path, dpi=150)
print(f"Saved comparison plot: {out_path}")
try:
    plt.show()
except Exception:
    pass
