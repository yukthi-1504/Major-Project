# Generates synthetic raw traffic and campaign data for the project
# trafficDataGenerator.py
import pandas as pd
import numpy as np

def generate_traffic_data(days=30, samples_per_hour=1, seed=42):
    np.random.seed(seed)
    
    total_samples = days * 24 * samples_per_hour
    timestamps = pd.date_range(start="2026-01-01", periods=total_samples, freq="h")

    
    # Features
    hour = timestamps.hour
    day_of_week = timestamps.dayofweek
    campaign = np.random.choice([0, 1], size=total_samples, p=[0.8, 0.2])
    discount = campaign * np.random.choice([10, 20, 30, 50], size=total_samples)
    
    # Base traffic (sinusoidal daily pattern + noise)
    base_traffic = 50 + 10 * np.sin(hour / 24 * 2 * np.pi) + 5 * np.random.randn(total_samples)
    past_traffic = pd.Series(base_traffic).rolling(3, min_periods=1).mean().values
    
    # Actual traffic: base + spike if campaign
    traffic = base_traffic + campaign * np.random.randint(50, 200, size=total_samples)
    
    # Create DataFrame
    df = pd.DataFrame({
        "timestamp": timestamps,
        "hour": hour,
        "day_of_week": day_of_week,
        "campaign": campaign,
        "discount": discount,
        "past_traffic": past_traffic,
        "traffic": traffic.astype(int)
    })
    
    return df

if __name__ == "__main__":
    df = generate_traffic_data()
    df.to_csv("synthetic_flashsale_data.csv", index=False)
    print("Synthetic traffic data generated and saved as 'synthetic_flashsale_data.csv'")
    print(df.head())
