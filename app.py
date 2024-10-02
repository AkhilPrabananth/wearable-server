from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np

app = FastAPI()

with open('isolation_forest_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

latest_results = {
    "timestamp": None,
    "heart_rate": None,
    "spo2": None,
    "predictions": None,
    "reason": None
}

def get_anomaly_reason(hr, spo2):
    hr_mean = 79.81708629223155
    hr_std = 15.853146562716525
    spo2_mean = 96.58683021304067
    spo2_std = 2.3738548827407393
    z_CI = 2.054 #96% confidence interval
    hr_lower_bound = hr_mean - (z_CI * hr_std)
    hr_upper_bound = hr_mean + (z_CI * hr_std)
    spo2_lower_bound = spo2_mean - (z_CI * spo2_std)
    reasons = []
    if spo2 < spo2_lower_bound:
        reasons.append("Low spO2")
    if hr < hr_lower_bound:
        reasons.append("Low HR")
    if hr > hr_upper_bound:
        reasons.append("High HR")
    if len(reasons) == 0:
        reasons.append("Unknown Reason")
    return reasons

#INPUT Format. Modify this if u want to add/change what gets sent
class DataInput(BaseModel):
    heart_rate: float
    spo2: float
    timestamp: str  

# API endpoint to update data and run the model
@app.post("/update/")
def update_data(data: DataInput):
    hr = data.heart_rate
    spo2 = data.spo2
    timestamp = data.timestamp

    features = np.array([[hr, spo2]])
    features_scaled = scaler.transform(features)

    # Run the model to get predictions (1 = normal, -1 = anomaly)
    predictions = model.predict(features_scaled)

    # Convert model's output: normal (0), anomaly (1)
    prediction_result = 1 if predictions[0] == -1 else 0

    # Update the latest results
    latest_results["timestamp"] = timestamp
    latest_results["heart_rate"] = hr
    latest_results["spo2"] = spo2
    latest_results["predictions"] = prediction_result

    if(latest_results["predictions"] == 0):
        latest_results["reason"] = ["No anomaly"]
    else:
        latest_results["reason"] = get_anomaly_reason(hr, spo2)
    
    return {
        "status": "Data updated",
        "heart_rate": hr,
        "spo2": spo2,
        "timestamp": timestamp,
        "predictions": prediction_result,
        "reason": latest_results["reason"]
    }

# API endpoint to get the latest prediction
@app.get("/latest/")
def get_latest():
    if latest_results["timestamp"] is None:
        return {"error": "No data available yet"}
    
    return {
        "timestamp": latest_results["timestamp"],
        "heart_rate": latest_results["heart_rate"],
        "spo2": latest_results["spo2"],
        "predictions": latest_results["predictions"],
        "reason": latest_results["reason"]
    }
