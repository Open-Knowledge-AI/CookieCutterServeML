from fastapi import APIRouter, HTTPException

from ..config import logger

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}
