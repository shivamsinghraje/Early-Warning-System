# python-ml/model_training.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from sklearn.metrics import mean_squared_error, mean_absolute_error
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import joblib
import os
from pathlib import Path
from typing import Tuple, Optional

class DeepANTTrainer:
    """DeepANT-based anomaly detection trainer"""

    def __init__(self, sequence_length: int = 10):
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = StandardScaler()

    def create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for time series prediction"""
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:i + self.sequence_length])
            y.append(data[i + self.sequence_length])
        return np.array(X), np.array(y)

    def build_model(self, input_shape: Tuple[int, int]) -> keras.Model:
        """Build DeepANT model architecture"""
        model = keras.Sequential([
            layers.Conv1D(filters=32, kernel_size=3, activation='relu',
                         input_shape=input_shape),
            layers.MaxPooling1D(pool_size=2),
            layers.Conv1D(filters=64, kernel_size=3, activation='relu'),
            layers.MaxPooling1D(pool_size=2),
            layers.Flatten(),
            layers.Dense(50, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(1)
        ])

        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model

    def train(self, df: pd.DataFrame, project_id: str,
              models_path: str, artifacts_path: str) -> Tuple[str, str, str]:
        """Train DeepANT model"""

        # Extract target column (assuming last column is target)
        target_col = df.columns[-1]
        data = df[target_col].values.reshape(-1, 1)

        # Scale data
        data_scaled = self.scaler.fit_transform(data)

        # Create sequences
        X, y = self.create_sequences(data_scaled)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Build and train model
        self.model = self.build_model((self.sequence_length, 1))

        history = self.model.fit(
            X_train, y_train,
            epochs=50,
            batch_size=32,
            validation_split=0.1,
            verbose=0
        )

        # Calculate reconstruction error threshold
        predictions = self.model.predict(X_test)
        mse = np.mean((predictions - y_test) ** 2, axis=1)
        threshold = np.percentile(mse, 95)  # 95th percentile as threshold

        # Create project directories
        project_models_dir = Path(models_path) / project_id
        project_artifacts_dir = Path(artifacts_path) / project_id
        project_models_dir.mkdir(parents=True, exist_ok=True)
        project_artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Save model and artifacts
        model_path = project_models_dir / "deepant_model.h5"
        scaler_path = project_artifacts_dir / "scaler.pkl"
        threshold_path = project_artifacts_dir / "threshold.pkl"

        self.model.save(str(model_path))
        joblib.dump(self.scaler, str(scaler_path))
        joblib.dump(threshold, str(threshold_path))

        return str(model_path), str(scaler_path), str(threshold_path)

class ForecastTrainer:
    """Time series forecasting model trainer"""

    def __init__(self, lookback: int = 24):
        self.lookback = lookback
        self.model = None
        self.scaler = StandardScaler()

    def create_dataset(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create dataset for forecasting"""
        X, y = [], []
        for i in range(self.lookback, len(data)):
            X.append(data[i-self.lookback:i])
            y.append(data[i])
        return np.array(X), np.array(y)

    def build_lstm_model(self, input_shape: Tuple[int, int]) -> keras.Model:
        """Build LSTM model for forecasting"""
        model = keras.Sequential([
            layers.LSTM(50, activation='relu', return_sequences=True,
                       input_shape=input_shape),
            layers.LSTM(50, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(25, activation='relu'),
            layers.Dense(1)
        ])

        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model

    def train(self, df: pd.DataFrame, project_id: str, models_path: str) -> str:
        """Train forecasting model"""

        # Extract features (all numeric columns)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        data = df[numeric_cols].values

        # Scale data
        data_scaled = self.scaler.fit_transform(data)

        # Use only target column for univariate forecasting
        target_data = data_scaled[:, -1].reshape(-1, 1)

        # Create dataset
        X, y = self.create_dataset(target_data)

        # Reshape for LSTM
        X = X.reshape((X.shape[0], X.shape[1], 1))

        # Split data
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # Build and train model
        self.model = self.build_lstm_model((self.lookback, 1))

        history = self.model.fit(
            X_train, y_train,
            epochs=50,
            batch_size=32,
            validation_data=(X_test, y_test),
            verbose=0
        )

        # Create project directory
        project_models_dir = Path(models_path) / project_id
        project_models_dir.mkdir(parents=True, exist_ok=True)

        # Save model
        model_path = project_models_dir / "forecast_model.h5"
        self.model.save(str(model_path))

        # Also save as joblib for compatibility
        joblib_path = project_models_dir / "forecast_model.pkl"
        joblib.dump(self.model, str(joblib_path))

        return str(model_path)