# Early Warning System (EWS)

A full-stack time-series anomaly detection and forecasting system built with Java Spring Boot, Python FastAPI, and vanilla JavaScript.

## Features

- **Data Cleaning**: Automated time-series data preprocessing
- **Anomaly Detection**: DeepANT-based anomaly detection
- **Forecasting**: LSTM-based time-series forecasting
- **Live Monitoring**: Real-time data fetching and analysis
- **Visualization**: Interactive plots with Plotly.js
- **Secure**: JWT-based authentication

## Technology Stack

- **Backend**: Java Spring Boot (MVC)
- **ML Service**: Python FastAPI
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Database**: MySQL
- **Visualization**: Plotly.js

## Quick Start

### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/your-repo/ews.git
cd ews

# Build and run with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8080
# ML Service: http://localhost:8001