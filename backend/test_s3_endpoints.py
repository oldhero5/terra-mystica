#!/usr/bin/env python3
"""
Test script for S3 image upload endpoints
"""

import os
import asyncio
import tempfile
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set environment variables for testing
os.environ["AWS_ACCESS_KEY_ID"] = "minioadmin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minioadmin"
os.environ["S3_BUCKET_NAME"] = "terra-mystica-images"
os.environ["S3_ENDPOINT_URL"] = "http://localhost:9000"
os.environ["AWS_REGION"] = "us-east-1"
os.environ["DATABASE_URL"] = "postgresql://terra_user:change_this_password@localhost:5432/terra_mystica"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

# Disable MCP for testing
os.environ["MCP_ENABLED"] = "false"

# Create a minimal FastAPI app for testing
from fastapi import FastAPI
from app.api.api_v1.endpoints.images_s3 import router as images_router
from app.core.config import settings

app = FastAPI(title="Test S3 Integration")
app.include_router(images_router, prefix="/api/v1/images", tags=["images"])

@app.get("/health")
async def health():
    return {"status": "ok", "s3_configured": bool(settings.S3_ENDPOINT_URL)}

def create_test_image() -> bytes:
    """Create a test image"""
    img = Image.new('RGB', (400, 300), color='blue')
    import io
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    return img_bytes.getvalue()

def test_s3_endpoints():
    """Test S3 endpoints"""
    client = TestClient(app)
    
    # Test health endpoint
    print("Testing health endpoint...")
    response = client.get("/health")
    print(f"Health response: {response.json()}")
    assert response.status_code == 200
    
    # Test presigned URL generation (no auth needed for this test)
    print("\nTesting presigned URL generation...")
    try:
        from app.services.s3 import s3_service
        
        # Test presigned POST
        presigned = s3_service.generate_presigned_post("test/sample.jpg")
        print(f"Presigned POST generated: {presigned['url']}")
        
        # Test presigned GET
        presigned_get = s3_service.generate_presigned_url("test/sample.jpg")
        print(f"Presigned GET generated: {presigned_get}")
        
    except Exception as e:
        print(f"Presigned URL test failed: {e}")
    
    print("\nS3 integration test completed!")

if __name__ == "__main__":
    test_s3_endpoints()