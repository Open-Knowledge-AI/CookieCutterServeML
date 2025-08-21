try:
    import tomllib
except ImportError:
    import tomli as tomllib  # For Python < 3.11 and Python > 3.6

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .api import health, predict, registry
from .core import RequestLoggingMiddleware
from .config import logger, ASSETS_DIR, PROJ_ROOT


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 FastAPI application starting...")
    yield
    logger.info("🛑 FastAPI application shutting down...")


app = FastAPI(
    lifespan=lifespan,
    title="ONNX AI Model Serving API",
    version="1.0.0",
    root_path="/api/v1",
)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(registry.router)
app.include_router(predict.router)
app.include_router(health.router)


#########################################
# Static file serving
#########################################
@app.get("/favicon.ico")
async def favicon():
    return FileResponse(ASSETS_DIR / "ico" / "onnxai-icon.ico")


##########################################
# Basic API Endpoints
##########################################
@app.get("/")
async def root():
    """
    Root endpoint that returns a welcome message.
    """
    return {"message": "Welcome to the ONNX AI Model Serving API!"}


@app.get("/version")
async def version():
    """
    Returns the current version of the application from pyproject.toml.
    """
    with open(PROJ_ROOT / "pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
    version_str = pyproject.get("project", {}).get("version", "unknown")
    return {"version": version_str}
