"""Aggregate real Olist order timestamps into hourly traffic counts.

Replaces the synthetic flash-sale traffic signal with a real one: each row
becomes one hour, and `traffic` is the count of real orders placed in that
hour. campaign/discount are dropped (Olist has no real promo signal, and we
decided not to fabricate one). The 2016-09..2016-12 and 2018-09..2018-10 tails
are trimmed — order volume in those months is near zero (data collection
ramping up / cutting off), not representative traffic.
"""
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
ORDERS_PATH = BASE_DIR / "external" / "olist_raw" / "olist_orders_dataset.csv"
OUT_PATH = BASE_DIR / "raw" / "olist_hourly_traffic.csv"

DENSE_START = "2017-01-01"
DENSE_END = "2018-08-31 23:59:59"

orders = pd.read_csv(ORDERS_PATH, parse_dates=["order_purchase_timestamp"])
orders = orders[
    (orders["order_purchase_timestamp"] >= DENSE_START)
    & (orders["order_purchase_timestamp"] <= DENSE_END)
]

hourly = (
    orders.set_index("order_purchase_timestamp")
    .resample("h")
    .size()
    .rename("traffic")
    .reset_index()
    .rename(columns={"order_purchase_timestamp": "timestamp"})
)

hourly["hour"] = hourly["timestamp"].dt.hour
hourly["day_of_week"] = hourly["timestamp"].dt.dayofweek
hourly["past_traffic"] = hourly["traffic"].shift(1).fillna(hourly["traffic"].mean())

hourly = hourly[["timestamp", "hour", "day_of_week", "past_traffic", "traffic"]]

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
hourly.to_csv(OUT_PATH, index=False)

print(f"Wrote {len(hourly)} hourly rows to {OUT_PATH}")
print(hourly.head())
print(f"traffic stats: mean={hourly['traffic'].mean():.2f}, "
      f"min={hourly['traffic'].min()}, max={hourly['traffic'].max()}")
