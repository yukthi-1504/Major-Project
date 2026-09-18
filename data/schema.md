# Data Schema Documentation

## Overview

All datasets in this project follow a standardized schema for e-commerce flash sale traffic prediction.

---

## Main Dataset: synthetic_flashsale_data.csv

### File Information
- **Location**: `data/raw/synthetic_flashsale_data.csv`
- **Format**: CSV (Comma-separated values)
- **Size**: 722 rows × 7 columns
- **Duration**: 30 days of hourly data (Jan 1-30, 2026)
- **Type**: Synthetic (artificially generated)

### Schema Definition

| Column Name | Data Type | Range | Unit | Description |
|------------|-----------|-------|------|-------------|
| timestamp | datetime | 2026-01-01 to 2026-01-31 | ISO 8601 | When the traffic occurred |
| hour | integer | 0-23 | hour of day | Hour of the day (0=midnight, 23=11PM) |
| day_of_week | integer | 0-6 | day code | Day of week (0=Monday, 6=Sunday) |
| campaign | binary | 0, 1 | flag | Is flash sale campaign active? |
| discount | integer | 0-50 | percentage | Discount percentage offered |
| past_traffic | float | 30-300 | requests | Traffic from the previous hour |
| traffic | integer | 30-300+ | requests | **TARGET** - Actual traffic (requests per hour) |

---

## Column Details

### timestamp
- **Type**: DateTime
- **Format**: `YYYY-MM-DD HH:MM:SS`
- **Example**: `2026-01-01 00:00:00`
- **Use**: Temporal reference for traffic event

### hour
- **Type**: Integer
- **Range**: 0-23
- **Distribution**: Uniform (24 hours repeating)
- **Pattern**: Traffic varies by hour (peak hours 10-12, 19-21)
- **Feature Use**: Captures time-of-day seasonality

### day_of_week
- **Type**: Integer
- **Range**: 0-6
- **Mapping**: 
  - 0 = Monday
  - 1 = Tuesday
  - 2 = Wednesday
  - 3 = Thursday
  - 4 = Friday
  - 5 = Saturday
  - 6 = Sunday
- **Pattern**: Weekend (5-6) may differ from weekdays (0-4)
- **Feature Use**: One-hot encoded to 7 binary features in ML model

### campaign
- **Type**: Binary Integer
- **Values**: 0 or 1
- **0 = No campaign** (normal traffic)
- **1 = Flash sale active** (expected traffic spike)
- **Effect**: ~3-4x traffic increase when active
- **Example Patterns**:
  - No campaign: traffic stays ~50-70
  - Campaign active: traffic jumps to 150-250

### discount
- **Type**: Integer
- **Range**: 0-50
- **Unit**: Percentage
- **Values**: 0, 10, 20, 30, 50
- **Correlation**: Higher discount → Higher traffic
- **Examples**:
  - 0% = 0 discount (no sale)
  - 20% = 20% off selected items
  - 50% = 50% off (mega sale)

### past_traffic
- **Type**: Float
- **Range**: 30-300
- **Unit**: Requests/hour
- **Definition**: Actual traffic from the previous hour
- **Use**: Captures traffic momentum/trend
- **Note**: Useful for lag features in time series prediction

### traffic (Target)
- **Type**: Integer
- **Range**: 35-300+
- **Unit**: Requests per hour
- **Distribution**: Right-skewed (more low values, few high peaks)
- **Examples**:
  - 54 requests = Slow hour (night)
  - 170 requests = Flash sale peak
  - 250 requests = Major flash sale
- **Relationship**:
  - `traffic = f(hour, day_of_week, campaign, discount, past_traffic)`
  - What the ML model predicts

---

## Data Quality

### Missing Values
- **None** - No missing values in synthetic data
- Production data may need handling

### Outliers
- **None** - Synthetic data is clean
- Real data should be checked and handled

### Data Validation Rules
```python
# Valid record checks:
assert 0 <= row['hour'] <= 23
assert 0 <= row['day_of_week'] <= 6
assert row['campaign'] in [0, 1]
assert 0 <= row['discount'] <= 50
assert row['past_traffic'] > 0
assert row['traffic'] > 0
```

---

## Data Statistics

### Summary Statistics
```
hour:            mean=11.5, min=0, max=23
day_of_week:     mean=3.0, min=0, max=6
campaign:        mean=0.33, unique=2 (33% have campaigns)
discount:        mean=6.7, min=0, max=50
past_traffic:    mean=85.3, std=42.1
traffic (target): mean=94.2, std=58.3, median=62
```

### Distribution Patterns

**Traffic Distribution** (without campaign):
```
Minimum: 30
25th percentile: 50
Median: 62
75th percentile: 100
Maximum: 300+
```

**Impact of Campaign:**
```
No campaign (campaign=0):
  Mean traffic: 60
  Std dev: 15

With campaign (campaign=1):
  Mean traffic: 200
  Std dev: 45
```

---

## Data Generation (How Synthetic Data Was Created)

The synthetic data was created with realistic e-commerce patterns:

### Base Traffic Model
```python
# Base traffic by hour (realistic e-commerce pattern)
base_traffic_by_hour = {
    0-5: 40-60 (night, low),
    6-9: 60-80 (morning),
    10-12: 80-120 (lunch peak),
    13-18: 70-100 (afternoon),
    19-21: 100-150 (evening peak),
    22-23: 50-80 (night)
}
```

### Campaign Effect Multiplier
```python
if campaign == 1:
    traffic *= 2.0 + (discount / 50)  # 2-3x traffic increase
```

### Noise & Variations
```python
# Random noise to make realistic
traffic += random_normal(0, 10)  # ±10 request variation
```

---

## Data Files & Structure

### Directory Layout
```
data/
├── raw/
│   ├── synthetic_flashsale_data.csv     # Main training data
│   ├── traffic_data_generator.py        # Script to generate data
│   └── README.md
├── processed/
│   └── (future: cleaned/transformed data)
├── schema.md                             # This file
└── README.md
```

### File Naming Convention
- `synthetic_flashsale_data.csv` - Original synthetic dataset
- `processed_*.csv` - Cleaned/processed versions (future)
- `test_*.csv` - Test datasets (future)

---

## Using This Data in Code

### Loading Data
```python
import pandas as pd

# Load data
df = pd.read_csv('data/raw/synthetic_flashsale_data.csv')

# Parse timestamps
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Check schema
print(df.dtypes)
print(df.head())
```

### Data Preparation
```python
# Feature engineering (as done in train_model.py)
df['lag_1'] = df['traffic'].shift(1)
df['lag_2'] = df['traffic'].shift(2)
df['rolling_mean_3'] = df['traffic'].rolling(3).mean()

# One-hot encode categorical
df = pd.get_dummies(df, columns=['day_of_week'])

# Split into features & target
X = df[feature_columns]
y = df['traffic']
```

---

## Data Privacy & Security

### Synthetic Data Advantages
- ✅ No real customer data
- ✅ Safe for sharing/open source
- ✅ No GDPR/privacy concerns
- ✅ Demonstrates patterns without risk

### Production Transition
When moving to real data:
- [ ] Anonymize personally identifiable information (PII)
- [ ] Aggregate to hourly/daily level
- [ ] Use differential privacy if needed
- [ ] Audit access logs
- [ ] Encrypt at rest

---

## Future Extensions

### Additional Features (For Production)
- **Weather data** - Affects shopping behavior
- **Day type** - Holiday, weekend, weekday
- **Marketing spend** - Correlation with traffic
- **External events** - Product launches, news
- **Competitor activity** - Market dynamics
- **Seasonal factors** - Month, quarter trends

### Data Sources
```
Internal:
├── Web server logs (click streams)
├── Payment gateway logs (transactions)
└── Inventory data (stock levels)

External:
├── Weather API
├── Holiday calendars
├── Social media trends
└── News APIs
```

---

## Schema Versioning

**Current Version**: 1.0
**Last Updated**: February 15, 2026

### Version History
- **v1.0** (Feb 15, 2026) - Initial schema with 7 columns

### Planned Changes
- **v1.1** (Future) - Add weather features
- **v1.2** (Future) - Add competitor data
- **v2.0** (Future) - Different time granularity (15 min vs hourly)

---

## Data Access & Permissions

### Current Status
- All data is synthetic (safe to share)
- No access restrictions
- Publicly available in repository

### Future Production Data
- Restricted access (need approval)
- Audit logging enabled
- Encryption in transit/at rest
- Regular backups

---

Last Updated: February 15, 2026
