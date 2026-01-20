import os
import json
import numpy as np
import pandas as pd
from typing import Tuple
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.layers import Conv1D, Dense, Flatten, Input
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from config import settings

def train_deepant_model(df: pd.DataFrame, project_name: str, datetime_col: str,
                        target_col: str, gnd_cols: list) -> Tuple[str, str, str]:


    # train for all columns - depending on your requirements

    # Train for target column
    model_path, threshold_path, scaler_path = train_deepant_model_for_column(
        df, target_col, project_name
    )

    return model_path, threshold_path, scaler_path


    #Train DeepAnT model for a specific column

def train_deepant_model_for_column(df: pd.DataFrame, column_name: str,
                                   project_name: str) -> Tuple[str, str, str]:

    # Create directories if they don't exist
    os.makedirs(settings.MODELS_PATH, exist_ok=True)
    os.makedirs(settings.ARTIFACTS_PATH, exist_ok=True)

    # Prepare data for the specific column
    column_data = df[column_name].values.reshape(-1, 1)

    # Remove NaN values for training
    column_data = column_data[~np.isnan(column_data).any(axis=1)]

    # Calculate quantiles for robust scaling
    q_min = np.percentile(column_data, 1)
    q_max = np.percentile(column_data, 99)

    # Scale data
    scaler = MinMaxScaler()
    scaler.fit([[q_min], [q_max]])
    scaled_data = scaler.transform(column_data)

    # Prepare sequences for training
    window_size = 12
    X, y = create_sequences(scaled_data, window_size)

    # Build DeepAnT model
    model = Sequential([
        #input_shape=(window_size, 1)
        Input(shape=(window_size, 1)),
        Conv1D(64, kernel_size=3, activation='relu'),
        Flatten(),
        Dense(50, activation='relu'),
        Dense(1)
    ])

    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

    # Train model
    model.fit(X, y, epochs=50, batch_size=32, validation_split=0.1,callbacks=[EarlyStopping(patience=5)], verbose=True)

    # Calculate threshold
    predictions = model.predict(X, verbose=0)
    errors = np.abs(predictions.flatten() - y)
    threshold = np.percentile(errors, 95)  # 95th percentile as threshold

    # Save model and artifacts with column-specific names
    model_filename = f"{project_name}_{column_name}_deepant.h5"
    threshold_filename = f"{project_name}_{column_name}_threshold.json"
    scaler_filename = f"{project_name}_{column_name}_scaler.json"

    model_path = os.path.join(settings.MODELS_PATH, model_filename)
    threshold_path = os.path.join(settings.ARTIFACTS_PATH, threshold_filename)
    scaler_path = os.path.join(settings.ARTIFACTS_PATH, scaler_filename)

    # Save model
    model.save(model_path)

    # Save threshold
    with open(threshold_path, 'w') as f:
        json.dump({"threshold": float(threshold)}, f)

    # Save scaler parameters
    with open(scaler_path, 'w') as f:
        json.dump({
            "q_min": float(q_min),
            "q_max": float(q_max),
            "column_name": column_name
        }, f)

    return model_path, threshold_path, scaler_path

#Create sequences for time series prediction
def create_sequences(data, window_size):

    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:i + window_size])
        y.append(data[i + window_size])
    return np.array(X), np.array(y).flatten()

#Train forecast model for the target column
def train_forecast_model(df: pd.DataFrame, project_name: str, datetime_col: str,
                         target_col: str) -> str:


    os.makedirs(settings.MODELS_PATH, exist_ok=True)

    # Prepare data
    df_sorted = df.sort_values(by=datetime_col)
    target_data = df_sorted[target_col].values.reshape(-1, 1)

    # Remove NaN values
    target_data = target_data[~np.isnan(target_data).any(axis=1)]

    # Scale data
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(target_data)

    # Prepare sequences
    window_size = 24  # Use last 24 points to predict next
    X, y = create_sequences(scaled_data, window_size)

    # Build forecast model
    model = Sequential([
        LSTM(128, activation='relu', input_shape=(window_size, 1), return_sequences=True),
        LSTM(64, activation='relu', return_sequences=True),
        LSTM(32, activation='relu'),
        Dense(16, activation='relu'),
        Dense(1)
    ])

    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])

    # Train model
    model.fit(X, y, epochs=100, batch_size=32, validation_split=0.2, verbose=0)

    # Save model and scaler
    model_filename = f"{project_name}_forecast.h5"
    scaler_filename = f"{project_name}_forecast_scaler.json"

    model_path = os.path.join(settings.MODELS_PATH, model_filename)
    scaler_path = os.path.join(settings.ARTIFACTS_PATH, scaler_filename)

    # Save model
    model.save(model_path)

    # Save scaler parameters
    with open(scaler_path, 'w') as f:
        json.dump({
            "min": float(scaler.data_min_[0]),
            "max": float(scaler.data_max_[0]),
            "window_size": window_size
        }, f)

    return model_path