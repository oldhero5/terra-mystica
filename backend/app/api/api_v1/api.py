"""
API v1 router configuration
"""

from fastapi import APIRouter
from app.api.api_v1.endpoints import health, auth, images_s3 as images, geolocation

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(geolocation.router, prefix="/geolocation", tags=["geolocation"])