from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse

from config import logger, ASSETS_DIR
from middleware import RequestLoggingMiddleware


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


@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
