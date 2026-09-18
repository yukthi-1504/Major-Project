# Predictive Autoscaling for Flash Sales

**Reva University Major Project** — a machine learning system that predicts e-commerce traffic
before it happens, and uses that prediction to scale infrastructure proactively instead of
reacting after the fact.

**🔗 Live API:** https://major-project-clj7.onrender.com/health
**📊 Live demo:** open [`dashboard.html`](dashboard.html) in any browser — it talks to the live API above.

> Free-tier hosting: the first request after ~15 minutes idle takes ~30-50s to wake the service
> back up. That's normal, not a bug.

---

## The problem

Flash sales cause sudden, sharp traffic spikes. Reactive autoscaling (the default in most
systems) only adds capacity *after* load already arrived — by then, users have already hit
timeouts and slow pages.

## The approach

Predict next-hour traffic first, then scale **ahead of** the spike:

```
Real order history (Olist e-commerce dataset)
        │
        ▼
Feature engineering (hour, day-of-week, lag/rolling traffic features)
        │
        ▼
Random Forest Regressor  →  predicted traffic for the next hour
        │
        ▼
Scaling rule  →  recommended replica count (1-5)
        │
        ▼
Flask REST API  (/predict, /health)
        │
        ├──▶ Deployed live on Render (this is the public URL above)
        │
        └──▶ Also deployable to Kubernetes, where an HPA reads real
             CPU/memory load and scales pods 1↔5 automatically
```

Both halves have been proven working, not just designed: the API is live on the public
internet right now, and the Kubernetes half has been run locally (Minikube) with the HPA
actually observed scaling pods up under real load and back down after.

---

## Project structure

```
.
├── api/app.py              Flask API — /health, /predict
├── ml/
│   ├── train_model.py      Trains the Random Forest model
│   ├── predict.py          Prediction helper used by the API
│   └── traffic_predictor.pkl
├── data/
│   ├── raw/olist_hourly_traffic.csv       Real data (default, aggregated from Olist)
│   └── raw/synthetic_flashsale_data.csv   Synthetic fallback dataset
│   └── external/olist_raw/                Original Olist CSVs the above was built from
├── k8s/deployment.yaml     Kubernetes Deployment + Service
├── k8s/hpa.yaml            HorizontalPodAutoscaler config
├── Dockerfile              Builds the API image (used both locally and by Render)
├── dashboard.html          Static browser demo UI, calls the live API
└── paper/                  IEEE-format writeup
```

---

## Try it right now

No setup needed — hit the live API directly:

```bash
curl https://major-project-clj7.onrender.com/health

curl -X POST https://major-project-clj7.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"current_time": "2026-02-15 10:00:00", "last_traffic": 40}'
```

Response:
```json
{
  "predicted_traffic": 38,
  "recommended_replicas": 2,
  "status": "success"
}
```

Or just open `dashboard.html` locally for a visual version of the same thing.

### Replica scaling rule

| Predicted traffic (requests/hour) | Recommended replicas |
|---|---|
| ≤ 10 | 1 |
| 11-25 | 2 |
| 26-50 | 3 |
| 51-80 | 4 |
| 80+ | 5 |

Tuned for real Olist-scale traffic (mean ~7 requests/hour, peaks ~104/hour in the dataset's
densest window) — much lower than the old synthetic thresholds this project started with.

---

## Running it yourself

### Locally (no Docker)

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

python ml/train_model.py      # trains on the real Olist data by default
python api/app.py             # serves on http://localhost:5000
```

Train on the synthetic dataset instead: `DATASET=synthetic python ml/train_model.py`.

### With Docker

```bash
docker build -t flashsale-app:latest .
docker run -p 5000:5000 flashsale-app:latest
curl http://localhost:5000/health
```

### On Kubernetes (proven working via Minikube)

```bash
minikube image load flashsale-app:latest      # if using Minikube
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/hpa.yaml

kubectl get hpa                                # watch it scale under load
kubectl port-forward svc/flashsale-app-service 8080:80
```

---

## The model

**Random Forest Regressor** (200 trees, max depth 10), trained on real Olist order data
aggregated into hourly traffic counts, with lag (1-3 hour) and rolling-average features plus
one-hot encoded day-of-week.

Evaluated on the chronologically last 20% of hours (a time-based split, not a random one —
random would leak future hours into training and make the model look better than it actually
is at forecasting):

| Metric | Model | Mean-predictor baseline | Improvement |
|---|---|---|---|
| MAE | 0.72 | 6 | 89% |
| RMSE | 1.85 | 8 | 77% |

A second model is also trained on the synthetic dataset, with a genuine campaign/discount
effect (dropped for the real model, since real Olist orders have no promo signal). The live
API serves both — pass `"mode": "synthetic"` to `/predict` to use it. The dashboard's
"Synthetic demo" toggle does exactly this.

---

## Deployment

- **Public API**: hosted free on [Render](https://render.com), built straight from this
  repo's `Dockerfile` on every push to `main`.
- **Kubernetes**: `k8s/deployment.yaml` + `k8s/hpa.yaml` describe the same app running with
  real autoscaling (CPU + memory triggered, 1-5 replicas) — proven locally via Minikube, not
  yet pointed at a public cluster.

---

## Status / what's next

- [x] Real-data model (swapped in from the original synthetic-only version)
- [x] Containerized API
- [x] Kubernetes HPA proven to scale live, both CPU- and memory-triggered
- [x] Public live deployment (Render)
- [x] Time-based train/test split (no data leakage)
- [x] Dual real/synthetic models with an honest campaign-effect demo
- [ ] Point the Kubernetes deployment at a real public cluster, not just local Minikube

---

**Author:** Yukthi P C — Reva University Major Project
