import pandas as pd
import numpy as np
import json
from typing import Tuple, Dict, Any, List
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import os
from config import settings

#Main function to clean time series data
def run_data_cleaning(df: pd.DataFrame, datetime_col: str, target_col: str,
                      gnd_cols: List[str], project_name: str) -> Tuple[pd.DataFrame, str]:


    from .model_training import train_deepant_model_for_column

    # Identifying all numeric columns to clean (target + gnd columns)
    numeric_cols = [target_col] + gnd_cols

    # Train DeepAnT models for each numeric column
    anomaly_configs = {}

    for col in numeric_cols:
        print(f"Training DeepAnT model for column: {col}")
        model_path, threshold_path, scaler_path = train_deepant_model_for_column(
            df, col, project_name
        )

        anomaly_configs[col] = {
            'model_path': model_path,
            'threshold_path': threshold_path,
            'scalers_path': scaler_path
        }

    # Now clean the data using your cleaning function
    cleaned_df, report = clean_time_series_data(
        df, datetime_col, anomaly_configs
    )

    return cleaned_df, report


def clean_time_series_data(df, datetime_col, anomaly_configs=None):

    # Initialize tracking variables for report
    original_rows = len(df)
    original_shape = df.shape
    duplicates_count = len(df) - len(df.drop_duplicates())
    original_missing = df.isnull().sum().sum()

    # Track changes per column
    column_stats = {}

    # Create a copy to avoid modifying original data
    df_clean = df.copy()

    # Identify float columns (excluding datetime column)
    float_cols = [col for col in df_clean.columns if col != datetime_col and
                  pd.api.types.is_numeric_dtype(df_clean[col])]

    # Initialize column statistics
    for col in float_cols:
        column_stats[col] = {
            'negative_values': 0,
            'zero_values': 0,
            'missing_before_first_fill': 0,
            'missing_after_first_fill': 0,
            'anomalies_detected': 0,
            'missing_after_anomaly': 0,
            'final_missing': 0
        }

    # Step 1: Remove duplicate rows
    df_clean = df_clean.drop_duplicates()
    rows_after_dedup = len(df_clean)

    # Step 2: Replace negative values with null in float columns
    for col in float_cols:
        negative_count = (df_clean[col] < 0).sum()
        column_stats[col]['negative_values'] = negative_count
        df_clean.loc[df_clean[col] < 0, col] = np.nan

    # Step 3: Replace 0 values with NaN for interpolation
    for col in float_cols:
        zero_count = (df_clean[col] == 0).sum()
        column_stats[col]['zero_values'] = zero_count
        df_clean.loc[df_clean[col] == 0, col] = np.nan

    # Step 4: First interpolation for null/nan/0 values
    for col in float_cols:
        missing_before = df_clean[col].isna().sum()
        column_stats[col]['missing_before_first_fill'] = missing_before
        df_clean[col] = df_clean[col].interpolate(method='linear', limit_direction='both')
        missing_after = df_clean[col].isna().sum()
        column_stats[col]['missing_after_first_fill'] = missing_after

    # Step 5: Detect anomalies for each float column (if configs provided)
    if anomaly_configs:
        for col in float_cols:
            if col in anomaly_configs:
                config = anomaly_configs[col]
                df_clean, anomaly_count = detect_anomalies_column(
                    df_clean,
                    col,
                    config['model_path'],
                    config['threshold_path'],
                    config['scalers_path']
                )
                column_stats[col]['anomalies_detected'] = anomaly_count
                column_stats[col]['missing_after_anomaly'] = df_clean[col].isna().sum()

    # Step 6: Second interpolation for anomaly-replaced nulls
    for col in float_cols:
        missing_before = df_clean[col].isna().sum()
        if missing_before > 0:
            df_clean[col] = df_clean[col].interpolate(method='linear', limit_direction='both')
        column_stats[col]['final_missing'] = df_clean[col].isna().sum()

    # Calculate final statistics
    final_rows = len(df_clean)
    final_missing = df_clean.isnull().sum().sum()
    total_values_cleaned = sum(
        stats['negative_values'] + stats['zero_values'] + stats['anomalies_detected']
        for stats in column_stats.values()
    )

    # Generate detailed report
    report = f"""
Data Cleaning Report

Overview:
---------
- Original shape: {original_shape}
- Final shape: {df_clean.shape}
- Original rows: {original_rows}
- Cleaned rows: {final_rows}
- Rows removed: {original_rows - final_rows}
- Duplicates removed: {duplicates_count}

Missing Values Summary:
----------------------
- Original missing values: {original_missing}
- Final missing values: {final_missing}
- Total values cleaned/filled: {total_values_cleaned}

Detailed Column Statistics:
--------------------------"""

    for col in float_cols:
        stats = column_stats[col]
        report += f"""
Column: {col}
  - Negative values replaced: {stats['negative_values']}
  - Zero values replaced: {stats['zero_values']}
  - Missing before first interpolation: {stats['missing_before_first_fill']}
  - Missing after first interpolation: {stats['missing_after_first_fill']}
  - Anomalies detected: {stats['anomalies_detected']}
  - Missing after anomaly detection: {stats['missing_after_anomaly']}
  - Final missing values: {stats['final_missing']}"""

    # Add processing summary
    report += f"""

Processing Summary:
------------------
1. Duplicate Removal: {duplicates_count} rows removed
2. Negative Value Handling: {sum(stats['negative_values'] for stats in column_stats.values())} values replaced with NaN
3. Zero Value Handling: {sum(stats['zero_values'] for stats in column_stats.values())} values replaced with NaN
4. First Interpolation: {sum(stats['missing_before_first_fill'] - stats['missing_after_first_fill'] for stats in column_stats.values())} values filled
5. Anomaly Detection: {sum(stats['anomalies_detected'] for stats in column_stats.values())} anomalies detected
6. Second Interpolation: {sum(stats['missing_after_anomaly'] - stats['final_missing'] for stats in column_stats.values())} anomaly values filled

Data Quality Improvement:
------------------------
- Data completeness: {((1 - final_missing / (df_clean.shape[0] * len(float_cols))) * 100):.2f}%
- Rows retained: {(final_rows / original_rows * 100):.2f}%
"""

    return df_clean, report


def detect_anomalies_column(df, column_name, model_path, threshold_path, scalers_path):
    """
    Your existing anomaly detection function - exactly as you wrote it
    """
    # Load model and configs for this specific column
    model = load_model(model_path, compile=False)
    window_size = 12

    with open(threshold_path) as f:
        threshold = json.load(f)["threshold"]

    with open(scalers_path) as f:
        cfg = json.load(f)
        col_scaler = MinMaxScaler()
        col_scaler.fit([[cfg["q_min"]], [cfg["q_max"]]])
        min_val = cfg["q_min"]
        max_val = cfg["q_max"]

    # Initialize variables for this column
    window = []
    anomaly_buffer = []
    consec_similar_anomalies = 0
    trend_shift_threshold = 5
    anomaly_count = 0

    result_df = df.copy()
    result_df[column_name] = result_df[column_name].astype(float)

    # Process each value in the column
    for idx, row in result_df.iterrows():
        val = row[column_name]

        # Skip if value is already NaN
        if pd.isna(val):
            continue

        scaled_val = col_scaler.transform([[val]])[0][0]

        # Build initial window
        if len(window) < window_size:
            if not window:
                # Initialize with slightly varied values
                rand_vals = np.random.uniform(0.96 * val, 1.04 * val,
                                              size=window_size - 1).reshape(-1, 1)
                window = list(col_scaler.transform(rand_vals).flatten())
            window.append(scaled_val)
            continue

        # Make prediction
        input_seq = np.array(window).reshape(1, window_size, 1)
        pred_scaled = model.predict(input_seq, verbose=0)[0][0]
        pred_val = col_scaler.inverse_transform([[pred_scaled]])[0][0]

        # Calculate error and determine status
        error = abs(scaled_val - pred_scaled)
        status = "Anomaly" if error > threshold else "Normal"

        if status == "Normal":
            # Update window for normal values
            window.pop(0)
            window.append(scaled_val)
            anomaly_buffer = []
            consec_similar_anomalies = 0

        elif status == "Anomaly":
            # Replace anomaly with NaN
            result_df.at[idx, column_name] = np.nan
            anomaly_count += 1

            # Handle consecutive similar anomalies
            value_similarity_range = 0.1 * val
            if not anomaly_buffer:
                anomaly_buffer = [val]
                consec_similar_anomalies = 1
            elif abs(val - np.mean(anomaly_buffer)) <= value_similarity_range:
                anomaly_buffer.append(val)
                consec_similar_anomalies += 1
            else:
                anomaly_buffer = [val]
                consec_similar_anomalies = 1

            # Trend shift detection
            if consec_similar_anomalies >= trend_shift_threshold:
                recent_scaled = col_scaler.transform(
                    np.array(anomaly_buffer[-window_size:]).reshape(-1, 1)
                ).flatten()
                window = window[-(window_size - len(recent_scaled)):] + list(recent_scaled)
                anomaly_buffer = []
                consec_similar_anomalies = 0

    return result_df, anomaly_count


#Generate plot data for original vs cleaned comparison for all columns
def generate_plot_data(original_df: pd.DataFrame, cleaned_df: pd.DataFrame,
                       datetime_col: str, target_col: str, gnd_cols: List[str]) -> Dict[str, Any]:


    # Get all numeric columns
    all_columns = [target_col] + gnd_cols

    # Prepare data structure for multiple columns
    original_y_data = {}
    cleaned_y_data = {}

    # Convert datetime column to string for JSON serialization
    datetime_str = original_df[datetime_col].astype(str).tolist()
    cleaned_datetime_str = cleaned_df[datetime_col].astype(str).tolist()

    # Collect data for each column
    for col in all_columns:
        if col in original_df.columns:
            # Handle NaN values by converting to None for JSON
            original_values = original_df[col].where(pd.notnull(original_df[col]), None).tolist()
            original_y_data[col] = original_values

        if col in cleaned_df.columns:
            # Handle NaN values by converting to None for JSON
            cleaned_values = cleaned_df[col].where(pd.notnull(cleaned_df[col]), None).tolist()
            cleaned_y_data[col] = cleaned_values

    # Create plot data structure
    plot_data = {
        "original": {
            "x": datetime_str,
            "y": original_y_data.get(target_col, []),  # Default to target column
            "y_columns": original_y_data,  # All columns data
            "name": "Original Data"
        },
        "cleaned": {
            "x": cleaned_datetime_str,
            "y": cleaned_y_data.get(target_col, []),  # Default to target column
            "y_columns": cleaned_y_data,  # All columns data
            "name": "Cleaned Data"
        }
    }

    return plot_data