import sys
from pathlib import Path
from datetime import datetime, timedelta

# --- Fix module import path for ML ---
BASE_DIR = Path(__file__).resolve().parent.parent  # MajorProjectReva
# Add project root so we can import the `ml` package reliably
sys.path.append(str(BASE_DIR))

from ml.predict import predict_next_hour, scale_replicas

# --- Try to import K8s client ---
try:
    from kubernetes import client, config
    K8S_AVAILABLE = True
except ImportError:
    K8S_AVAILABLE = False
    print("Kubernetes client not installed. Running in simulation mode.")

# --- CONFIG ---
current_time = datetime(2026, 2, 7, 0, 0)
last_traffic = 20  # starting traffic (real Olist scale, not synthetic 60+)

# K8s deployment config
NAMESPACE = "default"
DEPLOYMENT_NAME = "flashsale-app"

# --- Initialize K8s client if available ---
if K8S_AVAILABLE:
    try:
        config.load_kube_config()  # local kubeconfig
        apps_v1 = client.AppsV1Api()
        print("Kubernetes client loaded successfully.")
    except Exception as e:
        print("Failed to load Kubernetes config. Running in simulation mode.")
        K8S_AVAILABLE = False

# --- Simulation / Autoscale loop ---
print("Hour | Predicted Traffic | Recommended Replicas")
print("-----------------------------------------------")

for hour in range(24):
    predicted = predict_next_hour(current_time, last_traffic)
    replicas = scale_replicas(predicted)
    
    print(f"{current_time.hour:02d}   | {predicted:.0f}             | {replicas}")
    
    # --- Patch K8s deployment if client is available ---
    if K8S_AVAILABLE:
        # For safety: this script runs a local simulation by default.
        print("Kubernetes cluster not configured. Local simulation only.")
    
    # Update last traffic for next iteration
    last_traffic = predicted
    current_time += timedelta(hours=1)
