from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
import shutil
from pathlib import Path

from model_training import DeepANTTrainer, ForecastTrainer
from data_cleaning import DataCleaner
from schemas import CleanDataRequest, TrainRequest, PredictRequest

app = FastAPI(title="EWS ML Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage paths
STORAGE_PATH = Path("./storage")
MODELS_PATH = STORAGE_PATH / "models"
ARTIFACTS_PATH = STORAGE_PATH / "artifacts"
TEMP_PATH = STORAGE_PATH / "temp"

# Create directories
for path in [STORAGE_PATH, MODELS_PATH, ARTIFACTS_PATH, TEMP_PATH]:
    path.mkdir(parents=True, exist_ok=True)

@app.post("/clean-data")
async def clean_data(
    file: UploadFile = File(...),
    params: str = Form(...)
):
    """Clean time series data"""
    try:
        # Parse parameters
        clean_params = json.loads(params)

        # Save uploaded file
        temp_file = TEMP_PATH / f"{datetime.now().timestamp()}_{file.filename}"
        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)

        # Clean data
        cleaner = DataCleaner()
        result = cleaner.clean_data(
            str(temp_file),
            clean_params['datetime_col'],
            clean_params['target_col'],
            clean_params['gnd_cols']
        )

        # Clean up temp file
        os.remove(temp_file)

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/train-anomaly")
async def train_anomaly(request: TrainRequest):
    """Train DeepANT anomaly detection model"""
    try:
        trainer = DeepANTTrainer()

        # Load data
        df = pd.read_csv(request.data_path)

        # Train model
        model_path, scaler_path, threshold_path = trainer.train(
            df,
            request.project_id,
            str(MODELS_PATH),
            str(ARTIFACTS_PATH)
        )

        return {
            "model_path": model_path,
            "scaler_path": scaler_path,
            "threshold_path": threshold_path,
            "message": "Anomaly model trained successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/train-forecast")
async def train_forecast(request: TrainRequest):
    """Train forecasting model"""
    try:
        trainer = ForecastTrainer()

        # Load data
        df = pd.read_csv(request.data_path)

        # Train model
        model_path = trainer.train(
            df,
            request.project_id,
            str(MODELS_PATH)
        )

        return {
            "model_path": model_path,
            "message": "Forecast model trained successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict")
async def predict(request: PredictRequest):
    """Make prediction using trained models"""
    try:
        # Load models and artifacts
        project_models_path = MODELS_PATH / request.project_id
        project_artifacts_path = ARTIFACTS_PATH / request.project_id

        # Load anomaly detection components
        anomaly_model = joblib.load(project_models_path / "deepant_model.pkl")
        scaler = joblib.load(project_artifacts_path / "scaler.pkl")
        threshold = joblib.load(project_artifacts_path / "threshold.pkl")

        # Load forecast model
        forecast_model = joblib.load(project_models_path / "forecast_model.pkl")

        # Prepare data
        data_array = np.array(list(request.data.values())).reshape(1, -1)

        # Scale data
        data_scaled = scaler.transform(data_array)

        # Make predictions
        anomaly_score = anomaly_model.predict(data_scaled)[0]
        forecast_value = forecast_model.predict(data_scaled)[0]

        # Determine status
        status = "Anomaly" if anomaly_score > threshold else "Normal"

        return {
            "forecast": float(forecast_value),
            "anomaly_score": float(anomaly_score),
            "status": status,
            "threshold": float(threshold)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)