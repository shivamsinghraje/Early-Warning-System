# python-ml/data_cleaning.py
import pandas as pd
import numpy as np
from datetime import datetime
import os
from typing import List, Dict, Any

class DataCleaner:
    def __init__(self):
        self.cleaning_report = {}

    def clean_data(self, file_path: str, datetime_col: str,
                   target_col: str, gnd_cols: List[str]) -> Dict[str, Any]:
        """Clean time series data"""

        # Read data
        df = pd.read_csv(file_path)
        original_shape = df.shape

        # Initialize report
        self.cleaning_report = {
            "original_rows": original_shape[0],
            "original_cols": original_shape[1],
            "steps": []
        }

        # 1. Handle datetime column
        df[datetime_col] = pd.to_datetime(df[datetime_col], errors='coerce')
        df = df.dropna(subset=[datetime_col])
        self._add_step("Datetime parsing", df.shape[0])

        # 2. Sort by datetime
        df = df.sort_values(by=datetime_col)
        df = df.reset_index(drop=True)

        # 3. Handle duplicates
        df = df.drop_duplicates(subset=[datetime_col], keep='first')
        self._add_step("Remove duplicates", df.shape[0])

        # 4. Handle missing values in target column
        df[target_col] = pd.to_numeric(df[target_col], errors='coerce')

        # Forward fill then backward fill for target
        df[target_col] = df[target_col].fillna(method='ffill').fillna(method='bfill')

        # 5. Handle missing values in ground truth columns
        for col in gnd_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(method='ffill').fillna(method='bfill')

        # 6. Remove rows with any remaining NaN
        df = df.dropna()
        self._add_step("Remove NaN values", df.shape[0])

        # 7. Outlier detection and handling
        df = self._handle_outliers(df, target_col)
        self._add_step("Handle outliers", df.shape[0])

        # 8. Resample to regular intervals if needed
        df = self._resample_data(df, datetime_col, target_col, gnd_cols)

        # Save cleaned data
        cleaned_path = file_path.replace('.csv', '_cleaned.csv')
        df.to_csv(cleaned_path, index=False)

        # Generate before/after statistics
        stats = self._generate_statistics(df, target_col)

        return {
            "cleaned_path": cleaned_path,
            "cleaning_report": self.cleaning_report,
            "statistics": stats,
            "final_rows": df.shape[0],
            "final_cols": df.shape[1]
        }

    def _add_step(self, step_name: str, rows_after: int):
        """Add cleaning step to report"""
        self.cleaning_report["steps"].append({
            "step": step_name,
            "rows_after": rows_after
        })

    def _handle_outliers(self, df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """Handle outliers using IQR method"""
        Q1 = df[target_col].quantile(0.25)
        Q3 = df[target_col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Cap outliers instead of removing
        df[target_col] = df[target_col].clip(lower=lower_bound, upper=upper_bound)

        return df

    def _resample_data(self, df: pd.DataFrame, datetime_col: str,
                      target_col: str, gnd_cols: List[str]) -> pd.DataFrame:
        """Resample data to regular intervals"""
        df.set_index(datetime_col, inplace=True)

        # Determine frequency
        time_diffs = df.index.to_series().diff().dropna()
        most_common_freq = time_diffs.mode()[0]

        # Resample based on most common frequency
        if most_common_freq.total_seconds() < 3600:  # Less than 1 hour
            freq = '15T'  # 15 minutes
        elif most_common_freq.total_seconds() < 86400:  # Less than 1 day
            freq = 'H'  # Hourly
        else:
            freq = 'D'  # Daily

        # Resample
        resampled = df.resample(freq).agg({
            target_col: 'mean',
            **{col: 'mean' for col in gnd_cols if col in df.columns}
        })

        # Fill any gaps
        resampled = resampled.interpolate(method='linear')

        return resampled.reset_index()

    def _generate_statistics(self, df: pd.DataFrame, target_col: str) -> Dict[str, Any]:
        """Generate statistics for the cleaned data"""
        return {
            "mean": float(df[target_col].mean()),
            "std": float(df[target_col].std()),
            "min": float(df[target_col].min()),
            "max": float(df[target_col].max()),
            "missing_values": int(df[target_col].isna().sum())
        }