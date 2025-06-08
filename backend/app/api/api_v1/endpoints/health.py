"""
Health check endpoints
"""

from fastapi import APIRouter
from pydantic import BaseModel
import asyncio
import time

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: float
    checks: dict


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    
    checks = {
        "api": "healthy",
        "database": "unknown",  # Will implement database check later
        "redis": "unknown",     # Will implement redis check later
        "opensearch": "unknown" # Will implement opensearch check later
    }
    
    return HealthResponse(
        status="healthy",
        service="terra-mystica-api",
        version="0.1.0",
        timestamp=time.time(),
        checks=checks
    )


@router.get("/ready")
async def readiness_check():
    """Readiness probe for Kubernetes"""
    return {"status": "ready", "timestamp": time.time()}


@router.get("/live")
async def liveness_check():
    """Liveness probe for Kubernetes"""
    return {"status": "alive", "timestamp": time.time()}