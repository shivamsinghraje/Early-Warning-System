
CREATE DATABASE IF NOT EXISTS ews_db;
USE ews_db;

--Create tables
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL DEFAULT 'admin',
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(100) UNIQUE NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    datetime_col VARCHAR(255) NOT NULL,
    target_col VARCHAR(255) NOT NULL,
    gnd_cols JSON NOT NULL,
    is_live_enabled BOOLEAN DEFAULT FALSE,
    api_url VARCHAR(512),
    api_token VARCHAR(512),
    original_data_path VARCHAR(512),
    cleaned_data_path VARCHAR(512),
    anomaly_model_path VARCHAR(512),
    forecast_model_path VARCHAR(512),
    scaler_path VARCHAR(512),
    threshold_path VARCHAR(512),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS live_forecasts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    project_id_ref VARCHAR(100) NOT NULL,
    timestamp DATETIME NOT NULL,
    actual_value DOUBLE,
    forecasted_value DOUBLE NOT NULL,
    status ENUM('Normal', 'Anomaly') NOT NULL,
    FOREIGN KEY (project_id_ref) REFERENCES projects(project_id) ON DELETE CASCADE,
    INDEX (project_id_ref, timestamp)
);