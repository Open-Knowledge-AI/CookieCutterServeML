try:
    import tomllib
except ImportError:
    import tomli as tomllib  # For Python < 3.11 and Python > 3.6

from contextlib import asynccontextmanager

from fastapi.responses import FileResponse
from fastapi import FastAPI, Form, UploadFile, File, Request

from .middleware import RequestLoggingMiddleware
from .config import logger, ASSETS_DIR, PROJ_ROOT


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 FastAPI application starting...")
    yield
    logger.info("🛑 FastAPI application shutting down...")


app = FastAPI(lifespan=lifespan)
app.add_middleware(RequestLoggingMiddleware)


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(ASSETS_DIR / "ico" / "onnxai-icon.ico")


@app.get("/")
async def root():
    """
    Root endpoint that returns a welcome message.
    """
    return {"message": "Welcome to the ONNX AI Model Serving API!"}


@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}


@app.get("/version")
async def version():
    """
    Returns the current version of the application from pyproject.toml.
    """
    with open(PROJ_ROOT / "pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
    version_str = pyproject.get("project", {}).get("version", "unknown")
    return {"version": version_str}


@app.post("/predict")
async def predict(
    model_name: str = Form(...),
    input_data: UploadFile = File(...),
):
    content = await input_data.read()
    return {"model": model_name, "filename": input_data.filename, "size": len(content)}


@app.post("/predict-batch")
async def predict_batch(
    model_name: str = Form(...),
    input_files: list[UploadFile] = File(...),
):
    results = []
    for input_file in input_files:
        content = await input_file.read()
        results.append(
            {"model": model_name, "filename": input_file.filename, "size": len(content)}
        )
    return {"results": results}
