"""
Image upload and management endpoints with S3 integration
"""

import os
from typing import List, Optional
from datetime import datetime
import io

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.config import settings
from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.image import Image, ImageProcessingTask
from app.schemas.image import (
    ImageUploadResponse,
    ImageResponse,
    ImageListResponse,
    UploadProgress,
    PresignedUploadResponse
)
from app.utils.image_processing import ImageProcessor
from app.services.s3 import s3_service
from app.core.logging import logger

router = APIRouter()


@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ImageUploadResponse:
    """Upload a single image to S3"""
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Check file size
    if len(file_content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum of {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    # Validate image
    is_valid, error_msg = ImageProcessor.validate_image(file_content, file.content_type)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Generate unique filename
    filename = ImageProcessor.generate_filename(file.filename, current_user.id)
    base_key = f"images/{current_user.id}/{filename.rsplit('.', 1)[0]}"
    
    # Get image info from content
    image_info = ImageProcessor.get_image_info_from_bytes(file_content)
    
    # Extract EXIF data from content
    exif_data = ImageProcessor.extract_exif_data_from_bytes(file_content)
    
    # Upload to S3 with thumbnails
    try:
        urls = await s3_service.upload_image_with_thumbnails(
            file_content,
            base_key,
            file.content_type,
            metadata={
                "user_id": str(current_user.id),
                "original_filename": file.filename
            }
        )
    except Exception as e:
        logger.error(f"S3 upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image to storage"
        )
    
    # Create database record
    db_image = Image(
        user_id=current_user.id,
        filename=filename,
        original_filename=file.filename,
        content_type=file.content_type,
        file_size=len(file_content),
        file_path=urls.get("original", ""),
        s3_key=f"{base_key}_original.jpg",
        s3_url=urls.get("original", ""),
        thumbnail_small_url=urls.get("small", ""),
        thumbnail_medium_url=urls.get("medium", ""),
        thumbnail_large_url=urls.get("large", ""),
        width=image_info.get('width'),
        height=image_info.get('height'),
        exif_data=exif_data,
        exif_latitude=exif_data.get('gps_latitude'),
        exif_longitude=exif_data.get('gps_longitude'),
        exif_altitude=exif_data.get('gps_altitude'),
        status='uploaded'
    )
    
    # Handle EXIF datetime if available
    if 'DateTime' in exif_data:
        try:
            exif_datetime = datetime.strptime(exif_data['DateTime'], '%Y:%m:%d %H:%M:%S')
            db_image.exif_datetime = exif_datetime
        except:
            pass
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    logger.info(f"Image uploaded successfully to S3: {filename} by user {current_user.id}")
    
    return ImageUploadResponse.model_validate(db_image)


@router.post("/upload-multiple", response_model=List[ImageUploadResponse])
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[ImageUploadResponse]:
    """Upload multiple images to S3 (batch upload)"""
    
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 images can be uploaded at once"
        )
    
    uploaded_images = []
    
    for file in files:
        try:
            # Process each file using the single upload logic
            result = await upload_image(file, current_user, db)
            uploaded_images.append(result)
        except HTTPException as e:
            # Log error but continue with other files
            logger.error(f"Error uploading {file.filename}: {e.detail}")
            continue
    
    if not uploaded_images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No images were successfully uploaded"
        )
    
    return uploaded_images


@router.post("/presigned-upload", response_model=PresignedUploadResponse)
async def get_presigned_upload_url(
    filename: str,
    content_type: str,
    current_user: User = Depends(get_current_active_user)
) -> PresignedUploadResponse:
    """
    Get presigned URL for direct browser upload to S3.
    This allows the frontend to upload directly to S3 without going through the backend.
    """
    
    # Validate content type
    if not content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Generate unique filename
    unique_filename = ImageProcessor.generate_filename(filename, current_user.id)
    key = f"images/{current_user.id}/{unique_filename}"
    
    # Generate presigned POST data
    try:
        presigned_data = s3_service.generate_presigned_post(
            key=key,
            expiration=3600,  # 1 hour
            max_file_size=settings.MAX_UPLOAD_SIZE
        )
        
        return PresignedUploadResponse(
            upload_url=presigned_data["url"],
            fields=presigned_data["fields"],
            key=key,
            expires_in=3600
        )
    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate upload URL"
        )


@router.get("/", response_model=ImageListResponse)
def get_user_images(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ImageListResponse:
    """Get user's uploaded images with pagination"""
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Query total count
    total = db.query(Image).filter(
        and_(
            Image.user_id == current_user.id,
            Image.is_deleted == False
        )
    ).count()
    
    # Query images
    images = db.query(Image).filter(
        and_(
            Image.user_id == current_user.id,
            Image.is_deleted == False
        )
    ).order_by(Image.created_at.desc()).offset(offset).limit(per_page).all()
    
    # Generate presigned URLs for images if needed
    for image in images:
        if image.s3_key and not image.s3_url.startswith("http"):
            # Generate presigned URL with 1 hour expiration
            image.s3_url = s3_service.generate_presigned_url(image.s3_key, expiration=3600)
    
    return ImageListResponse(
        total=total,
        page=page,
        per_page=per_page,
        items=[ImageResponse.model_validate(img) for img in images]
    )


@router.get("/{image_id}", response_model=ImageResponse)
def get_image(
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ImageResponse:
    """Get a specific image"""
    
    image = db.query(Image).filter(
        and_(
            Image.id == image_id,
            Image.user_id == current_user.id,
            Image.is_deleted == False
        )
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Generate presigned URL if needed
    if image.s3_key and not image.s3_url.startswith("http"):
        image.s3_url = s3_service.generate_presigned_url(image.s3_key, expiration=3600)
    
    return ImageResponse.model_validate(image)


@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict:
    """Delete an image (soft delete)"""
    
    image = db.query(Image).filter(
        and_(
            Image.id == image_id,
            Image.user_id == current_user.id,
            Image.is_deleted == False
        )
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Soft delete
    image.is_deleted = True
    db.commit()
    
    # Optionally, delete from S3 (for hard delete)
    # await s3_service.delete_image_with_thumbnails(image.s3_key.rsplit('_', 1)[0])
    
    logger.info(f"Image soft deleted: {image.filename} by user {current_user.id}")
    
    return {"message": "Image deleted successfully"}


@router.websocket("/upload-progress")
async def upload_progress_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time upload progress"""
    await websocket.accept()
    
    try:
        while True:
            # Receive upload progress data
            data = await websocket.receive_json()
            
            # Validate data
            if "progress" not in data or "filename" not in data:
                await websocket.send_json({
                    "error": "Invalid progress data"
                })
                continue
            
            # Echo back progress (in production, this would track actual upload progress)
            await websocket.send_json({
                "filename": data["filename"],
                "progress": data["progress"],
                "status": "uploading" if data["progress"] < 100 else "completed"
            })
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")