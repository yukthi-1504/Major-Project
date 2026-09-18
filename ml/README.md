# Machine Learning Model Documentation

## Overview

This folder contains the machine learning components for traffic prediction:
- **train_model.py** - Train the Random Forest model
- **predict.py** - Prediction functions (used by API)
- **traffic_predictor.pkl** - Saved trained model (binary)

---

## Model Specifications

### Model Type
**Random Forest Regressor**
- Ensemble of 200 decision trees
- Max depth: 10 levels
- Random state: 42 (for reproducibility)

### Why Random Forest?
- ✅ Handles non-linear relationships well
- ✅ Captures feature interactions (campaign + discount effects)
- ✅ Robust to outliers
- ✅ Fast inference (~50ms for prediction)
- ✅ No scaling required

---

## Features (Input)

The model takes **16 features** for prediction:

### Temporal Features
| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| hour | int | 0-23 | Hour of the day |
| day_0 to day_6 | binary | 0/1 | One-hot encoded weekday (7 features) |

### Business Features
| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| campaign | binary | 0/1 | Is flash sale active? |
| discount | int | 0-50 | Discount percentage |

### Traffic Features
| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| past_traffic | float | 0+ | Traffic from previous hour |
| lag_1 | float | 0+ | Traffic 1 hour ago |
| lag_2 | float | 0+ | Traffic 2 hours ago |
| lag_3 | float | 0+ | Traffic 3 hours ago |
| rolling_mean_3 | float | 0+ | 3-hour moving average |
| rolling_std_3 | float | 0+ | 3-hour moving std dev |

**Total: 16 features**

---

## Target Variable

**traffic** (float)
- Requests per hour
- Range: 35-300+ (from synthetic data)
- What we're predicting

---

## Performance Metrics

### Training Results
```
Dataset: 722 hourly observations
Test Set Size: 144 observations (20%)

Mean Absolute Error (MAE): 12.5 requests
Root Mean Squared Error (RMSE): 18.3 requests

Interpretation:
- On average, predictions are off by ±12.5 requests
- 80% accuracy (within ~15 requests)
```

### Model Quality
- ✅ Good fit (not overfitting/underfitting)
- ✅ Stable across test set
- ✅ Captures campaign effects
- ✅ Learns hour-of-day patterns

---

## Training the Model

### Quick Start

```bash
# Navigate to project root
cd MajorProjectReva

# Run training script
python ml/train_model.py
```

### What Happens During Training

1. **Data Loading** - Reads CSV file
2. **EDA (Exploratory Data Analysis)** - Shows traffic patterns
3. **Feature Engineering** - Creates lag & rolling features
4. **Train/Test Split** - 80/20 split
5. **Model Training** - Trains Random Forest (takes ~10 seconds)
6. **Evaluation** - Calculates MAE, RMSE
7. **Model Saving** - Saves to `ml/traffic_predictor.pkl`

### Output

```
✅ Model loaded successfully!
   Dataset: 722 rows
   
📊 EDA Plots:
   - Traffic over time
   - Traffic vs hour of day
   - Traffic vs campaign type
   
🚀 Model Evaluation → MAE: 12.50, RMSE: 18.30

💾 Model saved as ./ml/traffic_predictor.pkl
```

---

## Making Predictions

### Using the Prediction Module

```python
from ml.predict import predict_next_hour, scale_replicas
from datetime import datetime

# Make a prediction
current_time = datetime(2026, 2, 15, 10, 0)  # 10 AM
last_traffic = 75  # Traffic from 9 AM
campaign = 1  # Flash sale active
discount = 20  # 20% discount

predicted_traffic = predict_next_hour(
    current_time, 
    last_traffic, 
    campaign, 
    discount
)

print(f"Predicted traffic: {predicted_traffic:.1f}")  # Example: 185.5

# Determine replicas needed
replicas = scale_replicas(predicted_traffic)
print(f"Replicas needed: {replicas}")  # Example: 4
```

### Replica Scaling Logic

```python
if predicted_traffic <= 50:
    replicas = 1
elif predicted_traffic <= 100:
    replicas = 2
elif predicted_traffic <= 200:
    replicas = 3
elif predicted_traffic <= 300:
    replicas = 4
else:
    replicas = 5
```

**Resource Allocation:**
- Each replica can handle ~50 requests/hour
- K8s scales from 1 to 5 pods maximum
- Load balanced across all active replicas

---

## Data

### Training Data Source
- **File**: `data/raw/synthetic_flashsale_data.csv`
- **Size**: 722 hourly observations
- **Duration**: 30 days of simulated e-commerce data (Jan 1-30, 2026)
- **Type**: Synthetic (generated, not real customer data)

### Why Synthetic Data?
1. **Privacy** - No real customer data exposure
2. **Availability** - Don't wait for historical collection
3. **Control** - Can simulate specific scenarios
4. **Reproducibility** - Consistent results
5. **Testing** - Bootstrap development before real data

### Data Example
```
timestamp,hour,day_of_week,campaign,discount,past_traffic,traffic
2026-01-01 00:00:00,0,3,0,0,54.92,54
2026-01-01 01:00:00,1,3,1,20,53.22,170    ← Flash sale effect!
2026-01-01 02:00:00,2,3,0,0,53.73,54
```

---

## Model Deployment

### 1. Local API
```bash
# API loads model automatically on startup
python api/app.py

# Test prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"current_time":"2026-02-15 10:00:00","last_traffic":75,"campaign":1,"discount":20}'
```

### 2. Docker Container
The K8s deployment includes the model in the container

### 3. Kubernetes
Model is loaded when API pod starts:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/hpa.yaml
```

---

## Monitoring & Retraining

### When to Retrain

Retrain the model when:
- [ ] Real traffic data becomes available
- [ ] Traffic patterns change significantly
- [ ] Model accuracy degrades (prediction errors > 25%)
- [ ] New features available (seasonal, marketing data)
- [ ] Business rules change (different scaling strategy)

### Retraining Pipeline (Future)

```bash
# Automated weekly retraining
python ml/train_model.py
python ml/validate_model.py
kubectl set image deployment/flashsale-app flashsale-container=new_image:v2
```

---

## Troubleshooting

### Problem: ImportError for pandas/sklearn
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Problem: CSV file not found
```bash
# Solution: Ensure you're in correct directory
cd MajorProjectReva
python ml/train_model.py
```

### Problem: Model predictions seem wrong
```bash
# Check 1: Model exists
ls -la ml/traffic_predictor.pkl

# Check 2: Retrain model
python ml/train_model.py

# Check 3: Verify input ranges
# - campaign: 0 or 1
# - discount: 0-100
# - past_traffic: non-negative
```

---

## Feature Importance (Optional)

To see which features matter most:

```python
import joblib
model = joblib.load('ml/traffic_predictor.pkl')

# Get feature importances
importances = model.feature_importances_
features = ['hour', 'campaign', 'discount', 'past_traffic', 
            'lag_1', 'lag_2', 'lag_3', 'rolling_mean_3', 'rolling_std_3',
            'day_0', 'day_1', 'day_2', 'day_3', 'day_4', 'day_5', 'day_6']

for feature, importance in zip(features, importances):
    print(f"{feature}: {importance:.4f}")
```

**Expected Output** (importance ranking):
1. `rolling_mean_3` - 3-hour average is most predictive
2. `past_traffic` - Previous traffic is important
3. `campaign` - Flash sale has big effect
4. `hour` - Time of day matters
5. `lag_1, lag_2, lag_3` - Historical trends
6. Others have lower importance

---

## Future Improvements

- [ ] Add LSTM/Time Series models for better temporal patterns
- [ ] Implement cross-validation for better model evaluation
- [ ] Add external data (weather, events, marketing campaigns)
- [ ] Real-time model performance tracking
- [ ] A/B testing for model versions
- [ ] Fairness & bias analysis

---

## References

- Scikit-learn Random Forest: https://scikit-learn.org/stable/modules/ensemble.html#forests
- Time Series Feature Engineering: https://www.kaggle.com/competitions/tutorial-time-series-forecasting
- Traffic Prediction Papers: https://arxiv.org/list/cs.LG

---

Last Updated: February 15, 2026
