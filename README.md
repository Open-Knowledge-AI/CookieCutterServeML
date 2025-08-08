# 🚀 CookieCutter MLServe (ONNX + FastAPI)

[![CCDS](https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter)](https://cookiecutter-data-science.drivendata.org/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://python.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=yellow)](https://pre-commit.com/)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://black.readthedocs.io/en/stable/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![ONNX](https://img.shields.io/badge/ONNX-1.16.0-005CED?logo=onnx)](https://onnx.ai/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.9.2-0984E3?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)

This repository provides a **production-ready starter template** for deploying machine learning models using **[ONNX](https://onnx.ai/)** as the primary model format.
It’s designed to help you get from a trained model to a running, API-served inference service **fast**, while keeping all the essentials for maintainability, observability, and scalability.

---

## ✨ Features

- **ONNX Model Serving** — Load and serve models in the ONNX format for portable, high-performance inference.
- **FastAPI** — High-speed, easy-to-use API server for inference requests.
- **Pydantic** — Strict request/response validation for reliable data handling.
- **Structured Logging** — Write meaningful, structured logs to files (request logs, system logs, errors).
- **User Request Tracking** — Automatically log each API request for monitoring and auditing.
- **Model Version Tracking** — Store and expose the deployed model version.
- **Dataset Version Tracking** — Keep track of which dataset version was used to train the deployed model.
- **Health Check Endpoint** — Quickly verify service readiness and liveness.
- **Configurable Settings** — Use environment variables for flexible deployments.
- **Docker-Ready** — Preconfigured `Dockerfile` for containerized deployment.

---

## 📂 Project Structure

```
.
├── app/
│   ├── main.py           # FastAPI entry point
│   ├── config.py         # Configuration & environment variables
│   ├── logger.py         # Logging setup
│   ├── models/
│   │   └── model.onnx    # Example ONNX model
│   ├── schemas/          # Pydantic request/response schemas
│   └── utils/            # Utility functions (e.g., version tracking)
├── logs/
│   ├── requests.log      # All incoming requests
│   └── system.log        # System and error logs
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

---

## ⚡ Getting Started

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Set Environment Variables
Copy the example environment file:
```bash
cp .env.example .env
```
Update `.env` with:
- `MODEL_PATH` — Path to your ONNX model.
- `MODEL_VERSION` — Version of your deployed model.
- `DATASET_VERSION` — Version of the dataset used to train the model.
- `LOG_DIR` — Directory where logs should be stored.

### 3️⃣ Run the Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The API will be available at:
➡️ `http://localhost:8000`

---

## 🛠 Example API Endpoints

| Method | Endpoint         | Description                          |
|--------|------------------|--------------------------------------|
| GET    | `/health`        | Check if the service is running.     |
| POST   | `/predict`       | Run inference on input data.         |
| GET    | `/metadata`      | Retrieve model and dataset versions. |

Example prediction request:
```json
POST /predict
Content-Type: application/json

{
  "feature1": 0.45,
  "feature2": 1.23,
  "feature3": 3.14
}
```

Example response:
```json
{
  "prediction": "class_A",
  "confidence": 0.92
}
```

---

## 📝 Logging

This repository uses **structured logging** for better observability:
- `logs/system.log` — Application startup, errors, and general info.
- `logs/requests.log` — Each incoming request, including timestamp and parameters.

Example system log:
```
2025-08-08 10:15:23 [INFO] Model loaded: model_v1.2.0.onnx
```

Example request log:
```
2025-08-08 10:16:05 [REQUEST] /predict - {"feature1":0.45,"feature2":1.23}
```

---

## 📦 Deployment

### Using Docker
```bash
docker build -t ml-deployment-starter .
docker run -p 8000:8000 ml-deployment-starter
```

---

## 🛡 Best Practices Included

✅ Versioned model & dataset metadata
✅ Validated API contracts using Pydantic
✅ Centralized configuration management
✅ Separation of concerns in code structure
✅ Logging for debugging and monitoring

---

## 📜 License

[LICENSE](LICENSE)

---

**💡 Tip:** This repo is a starting point — extend it with authentication, monitoring dashboards, or CI/CD integration for full production readiness.
