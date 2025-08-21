# 🚀 Serve-ML – Cookiecutter Starter for Serving Machine Learning Models

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker Ready](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)
[![Pre-commit Hooks](https://img.shields.io/badge/pre--commit-enabled-brightgreen)](https://pre-commit.com/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

---

A **production-ready starter template** for ML enthusiasts who want to **serve machine learning models without worrying about backend setup**.
This project is designed to **scale**, with best practices for logging, linting, code formatting, and containerization already built-in.

Whether you’re just prototyping or preparing for production, this repo gives you a **plug-and-play FastAPI server** for your models.

---

## 📂 Project Structure

```
open-knowledge-ai-cookiecutterserveml/
├── Dockerfile                  # Container setup
├── Makefile                    # Self-documented automation (lint, run, etc.)
├── pyproject.toml              # Project metadata + dev tooling configs
├── requirements.txt            # Python dependencies
├── .pre-commit-config.yaml     # Pre-commit hooks for clean code
└── app/
    ├── __init__.py
    ├── config.py               # Logging, environment, paths
    ├── main.py                 # FastAPI application entry
    └── middleware.py           # Custom request logging middleware
```

---

## ⚡ Features

- ✅ **FastAPI-based REST API** – lightweight, blazing-fast server
- ✅ **Model endpoints ready** – `/predict` and `/predict-batch` out of the box
- ✅ **Request logging** – structured logs with sensitive data filtering
- ✅ **Health & version endpoints** – `/health`, `/version`
- ✅ **Pre-commit hooks** – ensure clean code before pushing
- ✅ **Dockerized workflow** – build & run anywhere
- ✅ **Makefile automation** – simple commands for common tasks

---

## 🛠️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/open-knowledge-ai-cookiecutterserveml.git
cd open-knowledge-ai-cookiecutterserveml
```

### 2. Setup with Make

```bash
make env   # creates virtualenv, installs dependencies, sets up pre-commit hooks
make run   # starts FastAPI server at http://0.0.0.0:8000
```

### 3. Run with Docker

```bash
docker build -t serve-ml .
docker run -p 8000:8000 serve-ml
```

---

## 🌐 API Endpoints

| Endpoint         | Method | Description                           |
| ---------------- | ------ | ------------------------------------- |
| `/`              | GET    | Welcome message                       |
| `/health`        | GET    | Health check (returns `{status: ok}`) |
| `/version`       | GET    | Returns version from `pyproject.toml` |
| `/predict`       | POST   | Predict on a single file              |
| `/predict-batch` | POST   | Predict on multiple files             |

🔍 Example with `curl`:

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "model_name=my_model" \
  -F "input_data=@sample_input.json"
```

---

## 🧑‍💻 Development

### Formatting & Linting

```bash
make format   # auto-format with black
make lint     # check style with black + flake8
```

### Cleaning Build Files

```bash
make clean
```

### Pre-commit Hooks

Pre-commit ensures consistent formatting & hygiene:

```bash
make setup_hooks
```

---

## 📊 Logging

* Request logs → `logs/requests.log`
* System logs → `logs/system.log`

All logs are:

* Structured (JSON or formatted text)
* Rotated & compressed automatically
* Filtered (sensitive fields like `password`, `token` are masked)

---

## 📦 Requirements

* Python **3.11+**
* [FastAPI](https://fastapi.tiangolo.com/)
* [Uvicorn](https://www.uvicorn.org/)
* [Docker](https://www.docker.com/) (optional)

---

## 🚀 Roadmap

* [ ] Model registry integration
* [ ] ONNX/TensorFlow/PyTorch inference helpers
* [ ] Authentication & API keys
* [ ] Async batch processing
* [ ] Deployment templates (Kubernetes, AWS, etc.)

---

## 🤝 Contributing

Contributions are welcome 🎉!
Fork, open an issue, or submit a PR. Please run:

```bash
make format lint
```

before committing.

---

## 📜 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.
