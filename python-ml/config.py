import os
from pathlib import Path

class Settings:
    # Base paths
    BASE_DIR = Path(__file__).parent
    STORAGE_PATH = BASE_DIR / "storage"

    # Sub-directories
    MODELS_PATH = STORAGE_PATH / "models"
    ARTIFACTS_PATH = STORAGE_PATH / "artifacts"
    TEMP_PATH = STORAGE_PATH / "temp"
    DATA_PATH = STORAGE_PATH / "data"

    # Model parameters
    WINDOW_SIZE = 12
    FORECAST_WINDOW = 24
    ANOMALY_THRESHOLD_PERCENTILE = 95

    # Training parameters
    EPOCHS = 50
    BATCH_SIZE = 32
    LEARNING_RATE = 0.001

    # API settings
    MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

settings = Settings()