from fastapi import FastAPI
from pydantic import BaseModel
import sklearn
import pickle
import numpy as np
print(sklearn.__version__)
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
    "history": []  
}

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

    # Update the history to keep track of the last 3 results
    latest_results["history"].append(prediction_result)
    if len(latest_results["history"]) > 3:
        latest_results["history"].pop(0)

    # Check if the last 3 inputs were anomalies (all equal to 1)
    if latest_results["history"] == [1, 1, 1]:
        prediction_result = 2  # Set result to 2 if the last 3 were anomalies

    # Update the latest results
    latest_results["timestamp"] = timestamp
    latest_results["heart_rate"] = hr
    latest_results["spo2"] = spo2
    latest_results["predictions"] = prediction_result
    
    return {
        "status": "Data updated",
        "heart_rate": hr,
        "spo2": spo2,
        "timestamp": timestamp,
        "predictions": prediction_result 
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
        "predictions": latest_results["predictions"]
        #0 is normal, 1 means last input was an anomaly, 2 means last 3 inputs were anomalies
        #I suggesting using 2 for alerts so that it doesnt freak out basedd on 1 misreading
    }
