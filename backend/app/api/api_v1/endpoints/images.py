"""
Image upload and management endpoints
"""

import os
import aiofiles
from typing import List, Optional
from datetime import datetime

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
    UploadProgress
)
from app.utils.image_processing import ImageProcessor
from app.core.logging import logger

router = APIRouter()


@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ImageUploadResponse:
    """Upload a single image"""
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Check file size
    file_content = await file.read()
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
    
    # Save image to disk
    upload_dir = os.path.join(settings.UPLOAD_DIR, "images", str(current_user.id))
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, filename)
    
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)
    
    # Get image info
    image_info = ImageProcessor.get_image_info(file_path)
    
    # Extract EXIF data
    exif_data = ImageProcessor.extract_exif_data(file_path)
    
    # Create database record
    db_image = Image(
        user_id=current_user.id,
        filename=filename,
        original_filename=file.filename,
        content_type=file.content_type,
        file_size=len(file_content),
        file_path=file_path,
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
    
    # Create thumbnails asynchronously (in production, this would be a Celery task)
    # For now, we'll do it synchronously
    thumbnails = ImageProcessor.create_thumbnails(file_path, filename)
    
    # Update database with thumbnail paths
    for key, path in thumbnails.items():
        setattr(db_image, key, path)
    
    db.commit()
    db.refresh(db_image)
    
    logger.info(f"Image uploaded successfully: {filename} by user {current_user.id}")
    
    return ImageUploadResponse.model_validate(db_image)


@router.post("/upload-multiple", response_model=List[ImageUploadResponse])
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[ImageUploadResponse]:
    """Upload multiple images (batch upload)"""
    
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 images can be uploaded at once"
        )
    
    uploaded_images = []
    
    for file in files:
        try:
            # Process each file using the single upload logic
            # In production, this would be queued for async processing
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
    """Get specific image details"""
    
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
    
    return ImageResponse.model_validate(image)


@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict:
    """Soft delete an image"""
    
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
    image.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Image deleted successfully"}


@router.websocket("/upload-progress")
async def websocket_upload_progress(
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time upload progress"""
    await websocket.accept()
    
    try:
        while True:
            # Receive upload progress data
            data = await websocket.receive_json()
            
            # Echo back progress (in production, this would track actual upload)
            progress = UploadProgress(
                filename=data.get('filename', 'unknown'),
                bytes_uploaded=data.get('bytes_uploaded', 0),
                total_bytes=data.get('total_bytes', 0),
                percentage=data.get('percentage', 0),
                status=data.get('status', 'uploading')
            )
            
            await websocket.send_json(progress.model_dump())
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")


# Test endpoint for development
@router.post("/test-upload", response_model=dict)
async def test_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Test endpoint to verify upload functionality"""
    
    return {
        "message": "Upload test successful",
        "filename": file.filename,
        "content_type": file.content_type,
        "size": file.size,
        "user_id": current_user.id,
        "timestamp": datetime.utcnow().isoformat()
    }