# 🚀 Serve-ML – Starter Template for Serving Machine Learning Models

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker Ready](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)](https://www.docker.com/)
[![Pre-commit Hooks](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

---

A **production-ready starter template** for serving machine learning models with **FastAPI**.
This repo gives you a **plug-and-play ML API server** with best practices for:

- 📝 Structured logging
- 🐳 Containerization
- 🧹 Code quality (linting, formatting, pre-commit hooks)
- 📦 Registry of your models

Whether you’re just prototyping or preparing for production, this template saves you the backend setup hassle.

---

## 📂 Project Structure

```
src/
├── Dockerfile                  # Container setup
├── Makefile                    # Automation (lint, run, etc.)
├── pyproject.toml              # Metadata + dev tooling
├── requirements.txt            # Python dependencies
├── .pre-commit-config.yaml     # Pre-commit hooks
├── app/
│   ├── config.py               # Logging, env, paths
│   ├── main.py                 # FastAPI app entrypoint
│   ├── api/                    # API routers
│   │   ├── health.py           # /, /health, /version
│   │   ├── predict.py          # /predict, /predict-batch
│   │   └── registry.py         # /registry endpoints
│   └── core/                   # Middleware + registry backends
│       ├── middleware.py
│       └── registry.py
├── models/                     # ML model files live here
│   └──{dataset_version}/       # e.g., imagenet_v1/
│       └──{architecture}/      # e.g., resnet50/
│           └──{model_version}/ # e.g., v1/
│               └── model files # e.g. model.onnx, model.json
├── assets/                     # Static assets (e.g., favicon)
└── logs/                       # Rotating system & request logs
````

---

## ⚡ Features

* ✅ **FastAPI REST API** – blazing fast, async-ready
* ✅ **Model registry** – discover models via `/registry`
* ✅ **Inference endpoints** – `/predict` and `/predict-batch`
* ✅ **Health & version endpoints** – `/health`, `/version`
* ✅ **Structured logging** – with sensitive field filtering
* ✅ **Pre-commit hooks** – keep code clean before commits
* ✅ **Dockerized** – deploy anywhere
* ✅ **Makefile automation** – simple dev UX

---

## 🛠️ Getting Started

### 1. Clone the Repository (or Fork)

```bash
git clone https://github.com/Open-Knowledge-AI/CookieCutterServeML/
cd CookieCutterServeML
```

### 2. Setup with Make

```bash
make env   # create venv, install deps, setup hooks
make run   # start FastAPI at http://0.0.0.0:8000
```

### 3. Run with Docker

```bash
docker build -t serve-ml .
docker run -p 8000:8000 serve-ml
```

---

## 🌐 API Endpoints

| Endpoint                             | Method | Description                           |
|--------------------------------------| ------ | ------------------------------------- |
| `/`                                  | GET    | Welcome message                       |
| `/health`                            | GET    | Health check (returns `{status: ok}`) |
| `/version`                           | GET    | App version from `pyproject.toml`     |
| `/predict`                           | POST   | Predict on a single file              |
| `/predict/batch`                     | POST   | Predict on multiple files             |
| `/registry`                          | GET    | List all available models             |
| `/registry/{dataset}/{arch}/{model}` | GET    | Get details for a specific model      |

🔍 Example request:

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
make lint     # check style with flake8
```

### Cleaning Build Files

```bash
make clean
```

### Pre-commit Hooks

```bash
make setup_hooks
```

---

## 📊 Logging

* Request logs → `logs/requests.log`
* System logs → `logs/system.log`

Logs are:

* Structured (readable + JSON ready)
* Rotated & compressed automatically
* Sensitive fields (`password`, `token`, etc.) masked

---

## 📦 Requirements

* Python **3.11+**
* [FastAPI](https://fastapi.tiangolo.com/)
* [Uvicorn](https://www.uvicorn.org/)
* [Docker](https://www.docker.com/) (optional)

---

## Multi-Code Deployments
This template is also a plug-and-play solution for deploying multiple models with different codebases to test for performance and accuracy.
To use this feature, we make use of `git-tag-deploy`, a tool that allows you to deploy different git tags to different directories on the same server.

### Setup `git-tag-deploy`

1. Install `git-tag-deploy`:
    ```bash
    pip install git-tag-deploy
   ```
2. Create a configuration file `deployment.yaml` in the root of your project with the following structure:
    ```yaml
   deployments:
   - name: v0.2.1
     git_tag: v0.2.1
   - name: v0.2.0
     git_tag: v0.2.0
   - name: v0.1.0
     git_tag: v0.1.0
   ```
3. Simply run the following command to deploy all tags:
    ```bash
    git-tag-deploy
   ```
4. Access the deployment endpoints mapped using ports (example):
    - http://localhost:8001 for v0.2.1
    - http://localhost:8002 for v0.2.0
    - http://localhost:8003 for v0.1.0
    - http://localhost:5000/deployments for the deployment mapping
> ⚠️ **Experimental**: This feature is experimental and may not be suitable for production use. Use at your own risk.

> ⚠️ **Experimental**: git-tag-deploy is under active development and may have breaking changes in future releases.

> ⚠️ **Experimental**: this feature does not support docker deployments yet.

## 🚀 Roadmap

* [x] Basic project structure
* [x] Makefile for common tasks
* [x] Pre-commit hooks
* [x] Structured logging with rotation
* [x] Health & version endpoints
* [x] Single & batch prediction endpoints
* [x] Model registry endpoints
* [x] Dockerfile
* [x] Example model & inference logic
* [x] Environment variable configuration
* [x] Sensitive field filtering in logs
* [x] FastAPI serving template
* [x] Model registry (local filesystem)
* [ ] Multi-backend registry (S3, MLflow)
* [ ] Make a cookiecutter template from this repo
* [ ] Authentication & API keys
* [ ] Async batch processing
* [ ] Deployment templates (K8s, AWS, GCP)

---

## 🤝 Contributing

Contributions are welcome 🎉
Fork, open an issue, or submit a PR. Please run:

```bash
make format
```

before committing.

---

## 📜 License

This project is licensed under the **Apache 2.0 License** – see the [LICENSE](LICENSE) file for details.

---
