"""
Image-related Pydantic schemas
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class ImageBase(BaseModel):
    """Base image schema"""
    original_filename: str


class ImageUploadResponse(BaseModel):
    """Response after successful image upload"""
    id: int
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    width: Optional[int] = None
    height: Optional[int] = None
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ImageResponse(ImageUploadResponse):
    """Full image response with all details"""
    user_id: int
    file_path: str
    thumbnail_path: Optional[str] = None
    thumbnail_small_path: Optional[str] = None
    thumbnail_medium_path: Optional[str] = None
    
    # S3 URLs
    s3_key: Optional[str] = None
    s3_url: Optional[str] = None
    thumbnail_small_url: Optional[str] = None
    thumbnail_medium_url: Optional[str] = None
    thumbnail_large_url: Optional[str] = None
    
    # EXIF data
    exif_data: Optional[Dict[str, Any]] = None
    exif_latitude: Optional[float] = None
    exif_longitude: Optional[float] = None
    exif_altitude: Optional[float] = None
    exif_datetime: Optional[datetime] = None
    
    # Processing status
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Geolocation results
    predicted_latitude: Optional[float] = None
    predicted_longitude: Optional[float] = None
    confidence_score: Optional[float] = None
    alternative_locations: Optional[List[Dict[str, Any]]] = None
    
    updated_at: datetime


class ImageListResponse(BaseModel):
    """List of images with pagination"""
    total: int
    page: int
    per_page: int
    items: List[ImageResponse]


class ImageProcessingStatus(BaseModel):
    """WebSocket message for image processing status"""
    image_id: int
    status: str
    progress: int = Field(ge=0, le=100)
    current_step: Optional[str] = None
    message: Optional[str] = None
    
    
class ThumbnailSizes(BaseModel):
    """Configuration for thumbnail sizes"""
    small: tuple[int, int] = (150, 150)
    medium: tuple[int, int] = (400, 400)
    large: tuple[int, int] = (800, 800)


class UploadProgress(BaseModel):
    """WebSocket message for upload progress"""
    filename: str
    bytes_uploaded: int
    total_bytes: int
    percentage: int = Field(ge=0, le=100)
    status: str = "uploading"  # uploading, processing, completed, failed
    message: Optional[str] = None


class PresignedUploadResponse(BaseModel):
    """Response with presigned S3 upload data"""
    upload_url: str
    fields: Dict[str, str]
    key: str
    expires_in: int