# 🚨 Early Warning System (EWS) 

A production-inspired **Early Warning System** for dam discharge monitoring, forecasting, and anomaly detection — designed with a **Java Spring Boot backend**, a **Python-based ML microservice**, and a **lightweight vanilla JS frontend**.

This project is a functional mimic of a real Early Warning System I contributed to during my internship, refactored into a clean, modular, and production-aligned engineering solution.


## 💡 Project Motivation

During my internship at NHPC Limited, Faridabad, India, I contributed to a real-time Early Warning System for dam monitoring and automated safety alerts, where I worked on:
- Designing and enhancing **fault-tolerant RESTful backend APIs**
- Implementing **reliable service-layer logic** for alert processing
- Managing **real-time database workflows** for ingestion, validation, and processing of live dam data

That experience inspired me to recreate and extend the core ideas into this project — with a primary focus on backend engineering and system design, specifically:
- **Strong backend architecture** capable of handling real-time data flows
- **Clear separation of concerns** using MVC and microservices
- **Accurate forecasting** of dam discharge
- **Anomaly detection** to prevent misinformation

This system is intentionally built to resemble real-world production systems and engineering constraints, rather than simplified academic prototypes.

---

## 🧠 System Overview

The Early Warning System processes dam discharge data through a robust backend pipeline, validates and stores it in a database, and communicates with a Python ML service for forecasting and anomaly detection.

The results are then served to a lightweight frontend dashboard for monitoring and visualization.

```
[ Frontend (HTML / CSS / JS) ]
            ↓
[ Spring Boot Backend (MVC, REST APIs) ]
            ↓
[ MySQL Database ] ←→ [ Python ML Service (FastAPI) ]
```

---

## 🚀 Core Features

### 🔹 Backend (Java – Primary Focus)
- **RESTful API design** following Spring Boot MVC architecture
- **Layered structure**: Controller → Service → Repository
- **Fault-tolerant** request handling and validation
- **Secure authentication** using JWT
- **Clean separation** between business logic and data access

### 🔹 Forecasting & Anomaly Detection
- **Time-series forecasting** for dam discharge values
- **DeepANT-based anomaly detection** on forecasted data
- Prevents false alerts and misinformation by validating abnormal patterns
- ML logic isolated in a **Python FastAPI microservice**

### 🔹 Data Management
- **MySQL-backed** persistent storage
- **Optimized ingestion** and validation pipelines
- **Scalable schema design** for multiple projects and sensors

### 🔹 Frontend (Minimal, Purposeful)
- Built with **Vanilla JavaScript**, HTML, and CSS
- Focused on clarity and usability, not heavy frameworks
- **Real-time visualization** of discharge, forecasts, and anomalies

---

## 🛠 Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Java Spring Boot (MVC, REST) |
| **ML Service** | Python FastAPI |
| **Forecasting** | ANN |
| **Anomaly Detection** | DeepANT |
| **Database** | MySQL |
| **Frontend** | HTML, CSS, Vanilla JavaScript |
| **Visualization** | Plotly.js |
| **Auth** | JWT |
| **DevOps** | Docker, Docker Compose |

---

## 📁 Project Structure

```
early-warning-system/
│
├── spring-backend/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/
│   │   │   │   └── com/
│   │   │   │       └── ews/
│   │   │   │           ├── config/
│   │   │   │           ├── controller/
│   │   │   │           ├── service/
│   │   │   │           ├── model/
│   │   │   │           ├── repository/
│   │   │   │           ├── dto/
│   │   │   │           └── util/
│   │   │   └── resources/
│   │   │       ├── static/
│   │   │       └── templates/
│   │   └── test/
│   │       └── java/
│   └── docker/
│
├── python-ml/
│   ├── utils/
│
├── frontend/
│   ├── css/
│   ├── js/
│   └── assets/
│
├── storage/
│   ├── data/
│   ├── models/
│   ├── artifacts/
│   └── temp/
│
├── database/
│
├── nginx/
│
└── docs/

```

---

## ⚙️ Running the Project

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/shivamsinghraje/Early-Warning-System.git
cd ews

# Build and start all services
docker-compose up -d
```

### Option 2: Manual Setup

#### Prerequisites
- Java 17+
- Python 3.10+
- MySQL 8.0+
- Maven 3.6+

#### Backend Setup
```bash
cd spring-backend
mvn clean install
mvn spring-boot:run
```

#### Python ML Service
```bash
cd python-ml
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

#### Frontend
```bash
cd frontend
# Serve with any static server
python -m http.server 3000
```

### Services & Ports

| Service | Port |
|---------|------|
| Frontend | http://localhost:3000 |
| Spring Boot Backend | http://localhost:8080 |
| Python ML Service | http://localhost:8001 |
| MySQL | 3306 |

---

## 🔧 API Documentation

### Authentication Endpoints
```
POST   /api/auth/setup     - Initial admin setup
POST   /api/auth/login     - User login
POST   /api/auth/logout    - User logout
```

### Project Management
```
GET    /api/projects       - List all projects
POST   /api/projects/add   - Create new project
DELETE /api/projects/{id}  - Delete project
```

### Data Processing
```
POST   /api/process/clean-only              - Clean uploaded data
GET    /api/projects/{id}/historical-data   - Get historical data
GET    /api/projects/{id}/live-data         - Get live data
```

### Forecasting
```
POST   /api/forecast/live/{id}    - Fetch live data and predict
POST   /api/forecast/manual/{id}  - Manual prediction
GET    /api/forecast/history/{id} - Get forecast history
```

---

## 🔐 Security

- **JWT-based authentication**
- **Role-based access** (admin-only operations)
- **Protected endpoints** for forecasting and data processing
- **Password-protected** critical operations (project deletion)
- **CORS configured** for secure cross-origin requests

---

## 📊 Key Backend Design Patterns

### 1. **Layered Architecture**
```
Controller → Service → Repository → Database
```

### 2. **Dependency Injection**
- Constructor-based injection for testability
- Clear separation of concerns

### 3. **Exception Handling**
- Centralized error responses
- Consistent error format across APIs

### 4. **Data Transfer Objects (DTOs)**
- Clean API contracts
- Validation at entry points

---

## 🧪 Testing the System

1. **Setup Admin Account**
    - Navigate to http://localhost:3000/login.html
    - Create admin password (first-time setup)

2. **Upload Sample Data**
    - Use the "Clean Data" feature
    - Upload CSV/Excel with time-series data

3. **Create a Project**
    - Configure columns and parameters
    - Enable live monitoring (optional)

4. **View Dashboard**
    - Monitor real-time forecasts
    - Visualize anomalies
    - Track historical trends

---

## 📈 Why This Project Matters

This project demonstrates:
- **Strong Java backend fundamentals**
- **Real-world system design thinking**
- **Experience with microservices & inter-service communication**
- **Ability to translate industrial systems into scalable software**
- **Clean, readable, and maintainable code**

It reflects how I approach backend development: **reliability first, clarity always**.

---

## 🎯 Future Enhancements

- [ ] Implement WebSocket for real-time updates
- [ ] Add Kafka for event streaming
- [ ] Implement Redis caching layer
- [ ] Implement CI/CD pipeline


---

## 📜 License

MIT License

---

## ⭐ If you are reviewing this repository for a backend role:

Please focus on the **Spring Boot backend structure**, **service logic**, and **API design**, which were intentionally designed to reflect production-level practices.

Key files to review:
- `spring-backend/src/main/java/com/ews/service/` - Business logic implementation
- `spring-backend/src/main/java/com/ews/controller/` - RESTful API design
- `spring-backend/src/main/java/com/ews/config/` - Security and configuration


