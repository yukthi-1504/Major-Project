# MajorProjectReva: Predictive Autoscaling for Flash Sales

A production-ready machine learning system that predicts e-commerce traffic spikes and automatically scales Kubernetes infrastructure to handle flash sale events.

## 📋 Project Overview

This project implements an **intelligent autoscaling system** that:
- 📊 **Predicts traffic** for e-commerce flash sales using machine learning
- 🚀 **Auto-scales Kubernetes pods** based on predicted demand
- 🔄 **Exposes predictions via REST API** for external integrations
- 📉 **Minimizes infrastructure waste** by matching capacity to actual demand

### The Problem
Flash sales cause unpredictable traffic spikes. Traditional reactive autoscaling waits until traffic arrives, causing:
- ❌ Page timeouts
- ❌ Lost sales
- ❌ Bad user experience

### Our Solution
**Proactive autoscaling** - predict traffic 1 hour in advance and scale **before** the rush hits.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Flash Sale Event                           │
│         (Time, Campaign, Discount, etc.)                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              REST API (app.py - Flask)                      │
│  POST /predict, GET /health, GET /model-info, etc.         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│         ML Model (Random Forest Regressor)                  │
│   Trained on 30-day synthetic flash sale traffic data       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│         Prediction + Scaling Logic                          │
│   Traffic → Calculate Required Replicas                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│   Kubernetes HPA (Horizontal Pod Autoscaler)               │
│  Automatically scale pods based on CPU/Memory metrics       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  K8s Deployment (1-5 Flask API replicas)                   │
│     Serves predictions to load balancer                     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              External Clients                               │
│        (Dashboards, Mobile Apps, Monitoring Tools)         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
MajorProjectReva/
├── api/                          # REST API Service
│   ├── app.py                   # Flask API with endpoints
│   └── README.md                # API documentation
│
├── ml/                           # Machine Learning
│   ├── train_model.py           # Train Random Forest model
│   ├── predict.py               # Prediction functions
│   ├── traffic_predictor.pkl    # Trained model (binary)
│   └── README.md                # ML documentation
│
├── data/                         # Data Management
│   ├── raw/
│   │   ├── synthetic_flashsale_data.csv  # 30-day synthetic data
│   │   └── traffic_data_generator.py
│   ├── processed/              # (for future processed data)
│   ├── schema.md               # Data schema documentation
│   └── README.md
│
├── k8s/                          # Kubernetes Configuration
│   ├── deployment.yaml          # K8s deployment + service
│   ├── hpa.yaml                # Horizontal Pod Autoscaler config
│   ├── autoscale.py            # Standalone autoscaling script
│   └── README.md               # K8s documentation
│
├── dashboard.html              # Live demo UI (open in browser)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Kubernetes cluster (or local with Minikube)
- kubectl CLI
- Docker (optional, for containerization)

### 1️⃣ Setup Environment

```bash
# Clone/navigate to project
cd MajorProjectReva

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Train ML Model

```bash
# Train the Random Forest model on synthetic data
python ml/train_model.py

# Output: ml/traffic_predictor.pkl (trained model)
```

### 3️⃣ Test API Locally

```bash
# Start Flask API server
python api/app.py

# Server runs on: http://localhost:5000
```

### 4️⃣ Test Prediction Endpoints

**In another terminal:**

```bash
# Health check
curl http://localhost:5000/health

# Single prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "current_time": "2026-02-15 10:00:00",
    "last_traffic": 75,
    "campaign": 1,
    "discount": 20
  }'

# Batch predictions
curl -X POST http://localhost:5000/batch-predict \
  -H "Content-Type: application/json" \
  -d '{
    "predictions": [
      {"current_time": "2026-02-15 10:00:00", "last_traffic": 75, "campaign": 1, "discount": 20},
      {"current_time": "2026-02-15 11:00:00", "last_traffic": 150, "campaign": 1, "discount": 20}
    ]
  }'

# Get model info
curl http://localhost:5000/model-info

# Get API metrics
curl http://localhost:5000/metrics
```

### 5️⃣ Deploy to Kubernetes

```bash
# Apply deployment
kubectl apply -f k8s/deployment.yaml

# Apply HPA (requires Metrics Server)
kubectl apply -f k8s/hpa.yaml

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get svc

# Get service external IP
kubectl get service flashsale-app-service

# Access API (replace EXTERNAL-IP)
curl http://<EXTERNAL-IP>/health
```

---

## 📊 How It Works

### Input → Prediction → Action

```
Data Input:
├─ current_time: When the flash sale happens (hour of day)
├─ last_traffic: Traffic in the previous hour
├─ campaign: Is flash sale active? (0/1)
└─ discount: Discount percentage (0-50%)

        ↓ ML Model Prediction ↓

Predicted Output:
├─ predicted_traffic: Expected requests per hour
└─ recommended_replicas: How many K8s pods needed

        ↓ Kubernetes Acts ↓

Result:
└─ Pods scale automatically to handle load
```

### Scaling Rules

| Predicted Traffic | Replicas | Capacity per Replica |
|-------------------|----------|---------------------|
| 1-50              | 1        | 50 requests/hour     |
| 51-100            | 2        | 50 requests/pod      |
| 101-200           | 3        | 67 requests/pod      |
| 201-300           | 4        | 75 requests/pod      |
| 300+              | 5        | 60 requests/pod      |

---

## 🛠️ API Endpoints

### GET /health
**Purpose:** Check if API is running

**Response:** `{"status": "API is running", "model_loaded": true}`

---

### POST /predict
**Purpose:** Get traffic prediction and replica recommendation

**Request:**
```json
{
  "current_time": "2026-02-15 10:00:00",
  "last_traffic": 75,
  "campaign": 1,
  "discount": 20
}
```

**Response:**
```json
{
  "predicted_traffic": 185.5,
  "recommended_replicas": 4,
  "scaling_rule": "201-300 traffic → 4 replicas",
  "status": "success"
}
```

---

### POST /batch-predict
**Purpose:** Get predictions for multiple time periods

**Request:**
```json
{
  "predictions": [
    {"current_time": "2026-02-15 10:00:00", "last_traffic": 75, "campaign": 1, "discount": 20},
    {"current_time": "2026-02-15 11:00:00", "last_traffic": 150, "campaign": 1, "discount": 20}
  ]
}
```

**Response:** Array of predictions

---

### GET /model-info
**Response:** Model metadata (type, estimators, depth, etc.)

---

### GET /metrics
**Response:** API statistics and available endpoints

---

## 🤖 Machine Learning Model

### Model Type
**Random Forest Regressor** (200 trees, max depth 10)

### Features
- `hour` - Hour of day (0-23)
- `day_of_week` - Day of week (0-6)
- `campaign` - Flash sale active? (0/1)
- `discount` - Discount % (0-50)
- `past_traffic` - Previous hour traffic
- `lag_1, lag_2, lag_3` - Traffic from previous 3 hours
- `rolling_mean_3` - 3-hour rolling average
- `rolling_std_3` - 3-hour rolling std dev
- `day_0 to day_6` - One-hot encoded day of week

### Performance
```
Mean Absolute Error (MAE): ~12.5 requests
Root Mean Squared Error (RMSE): ~18.3 requests
Test Set Size: 20% of data
```

---

## 📈 Monitoring & Troubleshooting

### Check HPA Status
```bash
kubectl get hpa
kubectl describe hpa flashsale-app-hpa
```

### View Pod Metrics
```bash
kubectl top pods
kubectl top nodes
```

### Check API Logs
```bash
kubectl logs -f deployment/flashsale-app
```

### Common Issues

**Problem:** API returns "Model not loaded"
```bash
# Solution: Train the model first
python ml/train_model.py
```

**Problem:** HPA not scaling pods
```bash
# Check if Metrics Server is installed
kubectl get deployment metrics-server -n kube-system

# If not installed:
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

**Problem:** Cannot connect to API
```bash
# Check service
kubectl get svc flashsale-app-service

# Port forward for testing
kubectl port-forward svc/flashsale-app-service 5000:80
curl http://localhost:5000/health
```

---

## 📚 Documentation Files

- [API Documentation](api/README.md) - REST API endpoints and usage
- [ML Documentation](ml/README.md) - Model training and prediction
- [Data Documentation](data/schema.md) - Data schema and features
- [Kubernetes Guide](k8s/README.md) - Deployment and scaling configuration

---

## 🔮 Future Enhancements

- [ ] Real-time traffic data ingestion (replace synthetic data)
- [ ] Model retraining pipeline (automated weekly updates)
- [ ] Database integration (PostgreSQL for predictions history)
- [ ] Advanced HPA metrics (custom metrics from Prometheus)
- [ ] Grafana dashboards (visualization)
- [ ] Load testing (Apache JMeter/K6)
- [ ] Multi-region deployment
- [ ] CI/CD pipeline (GitHub Actions)

---

## 📝 License & Attribution

**Project Type:** Academic - Major Project for Reva University

**Team:** 
- Yukthi Gowda

**Technologies Used:**
- Python, Flask, scikit-learn, Kubernetes, Docker

---

## 📞 Support

For issues or questions:
1. Check the [Kubernetes troubleshooting guide](k8s/README.md)
2. Review [API documentation](api/README.md)
3. Check logs: `kubectl logs -f deployment/flashsale-app`

---

## ✅ Project Completion Status

- ✅ ML Model Training (train_model.py)
- ✅ Prediction Logic (predict.py)
- ✅ REST API (app.py with 5 endpoints)
- ✅ K8s Deployment (deployment.yaml + service)
- ✅ Horizontal Pod Autoscaler (hpa.yaml)
- ✅ Autoscaling Script (autoscale.py)
- ✅ Documentation (README files)
- ✅ Requirements (requirements.txt)

**Project Status: 100% COMPLETE** ✨

---

Last Updated: February 25, 2026
