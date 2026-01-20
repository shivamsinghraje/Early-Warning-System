from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
import shutil
from pathlib import Path
import tempfile

from schemas import CleanDataRequest, TrainRequest, PredictRequest
from data_cleaning import run_data_cleaning, generate_plot_data
from model_training import train_deepant_model, train_forecast_model
from config import settings

app = FastAPI(title="EWS ML Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
for path in [settings.STORAGE_PATH, settings.MODELS_PATH,
             settings.ARTIFACTS_PATH, settings.TEMP_PATH, settings.DATA_PATH]:
    Path(path).mkdir(parents=True, exist_ok=True)

@app.post("/clean-data")
async def clean_data(
        file: UploadFile = File(...),
        params: str = Form(...)
):
    """Clean time series data"""
    temp_file = None
    try:
        # Parse parameters
        clean_params = json.loads(params)

        # Validate required parameters
        required_fields = ['datetime_col', 'target_col', 'gnd_cols', 'project_name', 'project_id']
        for field in required_fields:
            if field not in clean_params:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # Save uploaded file
        temp_file = Path(settings.TEMP_PATH) / f"{datetime.now().timestamp()}_{file.filename}"
        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)

        # Read CSV
        df = pd.read_csv(temp_file)

        # Validate columns exist
        datetime_col = clean_params['datetime_col']
        target_col = clean_params['target_col']
        gnd_cols = clean_params['gnd_cols']

        missing_cols = []
        if datetime_col not in df.columns:
            missing_cols.append(datetime_col)
        if target_col not in df.columns:
            missing_cols.append(target_col)
        for col in gnd_cols:
            if col not in df.columns:
                missing_cols.append(col)

        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns in file: {', '.join(missing_cols)}"
            )

        # Convert datetime column
        df[datetime_col] = pd.to_datetime(df[datetime_col])

        # Run cleaning
        cleaned_df, report = run_data_cleaning(
            df,
            datetime_col,
            target_col,
            gnd_cols,
            clean_params['project_name']
        )

        # Save cleaned data
        project_data_dir = Path(settings.DATA_PATH) / clean_params['project_id']
        project_data_dir.mkdir(parents=True, exist_ok=True)

        cleaned_path = project_data_dir / f"{clean_params['project_id']}_cleaned.csv"
        cleaned_df.to_csv(cleaned_path, index=False)

        # Generate plot data
        plot_data = generate_plot_data(df, cleaned_df, datetime_col, target_col, gnd_cols)

        # Calculate statistics
        stats = {
            "mean": float(cleaned_df[target_col].mean()),
            "std": float(cleaned_df[target_col].std()),
            "min": float(cleaned_df[target_col].min()),
            "max": float(cleaned_df[target_col].max()),
            "missing_values": int(cleaned_df[target_col].isna().sum())
        }

        return {
            "cleaned_path": str(cleaned_path),
            "cleaning_report": {
                "original_rows": len(df),
                "final_rows": len(cleaned_df),
                "report_text": report,
                "steps": [
                    {"step": "Data loaded", "rows_after": len(df)},
                    {"step": "Cleaning completed", "rows_after": len(cleaned_df)}
                ]
            },
            "statistics": stats,
            "plot_data": plot_data,
            "final_rows": len(cleaned_df),
            "final_cols": len(cleaned_df.columns)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Clean up temp file
        if temp_file and temp_file.exists():
            os.remove(temp_file)

@app.post("/train-anomaly")
async def train_anomaly(request: TrainRequest):
    """Train DeepANT anomaly detection model"""
    try:
        # Load data
        df = pd.read_csv(request.data_path)

        # Get column configuration from the cleaned data
        # Assuming datetime is first column, target is last, and rest are gnd_cols
        columns = df.columns.tolist()
        datetime_col = columns[0]  # You might want to pass this explicitly
        target_col = columns[-1]    # You might want to pass this explicitly
        gnd_cols = columns[1:-1]    # You might want to pass this explicitly

        # Train model
        model_path, threshold_path, scaler_path = train_deepant_model(
            df,
            request.project_id,
            datetime_col,
            target_col,
            gnd_cols
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
        # Load data
        df = pd.read_csv(request.data_path)

        # Get column configuration
        columns = df.columns.tolist()
        datetime_col = columns[0]
        target_col = columns[-1]

        # Train model
        model_path = train_forecast_model(
            df,
            request.project_id,
            datetime_col,
            target_col
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
        # For now, return mock prediction
        # In production, you would load the models and make actual predictions

        # Mock implementation
        value = list(request.data.values())[0] if request.data else 100.0

        # Simulate prediction
        forecast_value = value * np.random.uniform(0.95, 1.05)
        anomaly_score = np.random.uniform(0, 1)
        threshold = 0.7
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

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download cleaned file"""
    # Search for file in data directories
    for root, dirs, files in os.walk(settings.DATA_PATH):
        if filename in files:
            file_path = os.path.join(root, filename)
            return FileResponse(
                path=file_path,
                filename=filename,
                media_type='text/csv'
            )

    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)