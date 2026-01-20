from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class CleanDataRequest(BaseModel):
    datetime_col: str
    target_col: str
    gnd_cols: List[str]
    project_name: str
    project_id: str

class TrainRequest(BaseModel):
    project_id: str
    data_path: str

class PredictRequest(BaseModel):
    project_id: str
    data: Dict[str, float]

class CleanDataResponse(BaseModel):
    cleaned_path: str
    cleaning_report: Dict[str, Any]
    statistics: Dict[str, float]
    plot_data: Dict[str, Any]
    final_rows: int
    final_cols: int

class TrainResponse(BaseModel):
    model_path: str
    message: str
    additional_paths: Optional[Dict[str, str]] = None

class PredictResponse(BaseModel):
    forecast: float
    anomaly_score: float
    status: str
    threshold: float