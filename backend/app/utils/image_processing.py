"""
Image processing utilities for handling uploads, thumbnails, and EXIF data
"""

import os
import hashlib
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime
import json
from io import BytesIO

from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
import pillow_heif  # Support for HEIF/HEIC formats

from app.core.config import settings
from app.core.logging import logger


# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()


class ImageProcessor:
    """Handle image processing operations"""
    
    THUMBNAIL_SIZES = {
        'small': (150, 150),
        'medium': (400, 400),
        'large': (800, 800)
    }
    
    @staticmethod
    def validate_image(file_content: bytes, content_type: str) -> Tuple[bool, Optional[str]]:
        """Validate image file"""
        try:
            # Check file size
            if len(file_content) > settings.MAX_UPLOAD_SIZE:
                return False, f"File size exceeds maximum of {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            
            # Check content type
            if content_type:
                mime_type = content_type.split('/')[1].lower()
                if mime_type not in settings.ALLOWED_EXTENSIONS:
                    return False, f"File type {mime_type} not allowed"
            
            # Try to open image
            image = Image.open(BytesIO(file_content))
            image.verify()
            
            return True, None
            
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    @staticmethod
    def generate_filename(original_filename: str, user_id: int) -> str:
        """Generate unique filename"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        file_ext = Path(original_filename).suffix.lower()
        
        # Create hash of original filename + timestamp
        hash_input = f"{original_filename}{timestamp}{user_id}".encode()
        file_hash = hashlib.md5(hash_input).hexdigest()[:8]
        
        return f"{timestamp}_{user_id}_{file_hash}{file_ext}"
    
    @staticmethod
    def save_image(file_content: bytes, filename: str, directory: str) -> str:
        """Save image to disk"""
        file_path = os.path.join(directory, filename)
        
        # Ensure directory exists
        os.makedirs(directory, exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path
    
    @staticmethod
    def create_thumbnails(image_path: str, filename: str) -> Dict[str, str]:
        """Create multiple thumbnail sizes"""
        thumbnails = {}
        
        try:
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img
                
                for size_name, dimensions in ImageProcessor.THUMBNAIL_SIZES.items():
                    # Create thumbnail
                    thumb = img.copy()
                    thumb.thumbnail(dimensions, Image.Resampling.LANCZOS)
                    
                    # Generate thumbnail filename
                    name_parts = filename.split('.')
                    thumb_filename = f"{'.'.join(name_parts[:-1])}_{size_name}.{name_parts[-1]}"
                    
                    # Save thumbnail
                    thumb_path = os.path.join(settings.THUMBNAIL_DIR, thumb_filename)
                    os.makedirs(settings.THUMBNAIL_DIR, exist_ok=True)
                    
                    thumb.save(thumb_path, quality=85, optimize=True)
                    thumbnails[f"thumbnail_{size_name}_path"] = thumb_path
                    
        except Exception as e:
            logger.error(f"Error creating thumbnails: {str(e)}")
            
        return thumbnails
    
    @staticmethod
    def extract_exif_data(image_path: str) -> Dict[str, Any]:
        """Extract EXIF data from image"""
        exif_data = {}
        
        try:
            with Image.open(image_path) as img:
                # Get basic image info
                exif_data['width'] = img.width
                exif_data['height'] = img.height
                exif_data['format'] = img.format
                
                # Extract EXIF data
                exifdata = img.getexif()
                
                if exifdata:
                    # Convert EXIF data to readable format
                    for tag_id, value in exifdata.items():
                        tag = TAGS.get(tag_id, tag_id)
                        
                        # Convert value to JSON-serializable format
                        value = ImageProcessor._make_json_serializable(value)
                        
                        exif_data[tag] = value
                    
                    # Extract GPS data if available
                    gps_info = exifdata.get_ifd(ExifTags.IFD.GPSInfo)
                    if gps_info:
                        gps_data = {}
                        for key, val in gps_info.items():
                            decode = GPSTAGS.get(key, key)
                            gps_data[decode] = ImageProcessor._make_json_serializable(val)
                        
                        # Convert GPS coordinates
                        lat, lon, alt = ImageProcessor._convert_gps_coordinates(gps_data)
                        if lat and lon:
                            exif_data['gps_latitude'] = lat
                            exif_data['gps_longitude'] = lon
                            if alt:
                                exif_data['gps_altitude'] = alt
                        
                        exif_data['gps_data'] = gps_data
                
        except Exception as e:
            logger.error(f"Error extracting EXIF data: {str(e)}")
        
        return exif_data
    
    @staticmethod
    def _make_json_serializable(value):
        """Convert values to JSON-serializable format"""
        # Handle bytes
        if isinstance(value, bytes):
            return value.decode('utf-8', errors='ignore')
        
        # Handle PIL IFDRational
        if hasattr(value, 'numerator') and hasattr(value, 'denominator'):
            if value.denominator != 0:
                return float(value.numerator) / float(value.denominator)
            else:
                return float(value.numerator)
        
        # Handle tuples and lists
        if isinstance(value, (tuple, list)):
            return [ImageProcessor._make_json_serializable(item) for item in value]
        
        # Handle dictionaries
        if isinstance(value, dict):
            return {k: ImageProcessor._make_json_serializable(v) for k, v in value.items()}
        
        # Handle other non-serializable types
        if not isinstance(value, (str, int, float, bool, type(None))):
            return str(value)
        
        return value
    
    @staticmethod
    def _convert_gps_coordinates(gps_data: Dict) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Convert GPS coordinates from EXIF format to decimal degrees"""
        try:
            # Latitude
            lat = None
            if 'GPSLatitude' in gps_data and 'GPSLatitudeRef' in gps_data:
                lat_deg = gps_data['GPSLatitude']
                lat = lat_deg[0] + lat_deg[1] / 60.0 + lat_deg[2] / 3600.0
                if gps_data['GPSLatitudeRef'] == 'S':
                    lat = -lat
            
            # Longitude
            lon = None
            if 'GPSLongitude' in gps_data and 'GPSLongitudeRef' in gps_data:
                lon_deg = gps_data['GPSLongitude']
                lon = lon_deg[0] + lon_deg[1] / 60.0 + lon_deg[2] / 3600.0
                if gps_data['GPSLongitudeRef'] == 'W':
                    lon = -lon
            
            # Altitude
            alt = None
            if 'GPSAltitude' in gps_data:
                alt = float(gps_data['GPSAltitude'])
                if 'GPSAltitudeRef' in gps_data and gps_data['GPSAltitudeRef'] == 1:
                    alt = -alt
            
            return lat, lon, alt
            
        except Exception as e:
            logger.error(f"Error converting GPS coordinates: {str(e)}")
            return None, None, None
    
    @staticmethod
    def get_image_info(image_path: str) -> Dict[str, Any]:
        """Get basic image information"""
        try:
            with Image.open(image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode
                }
        except Exception as e:
            logger.error(f"Error getting image info: {str(e)}")
            return {}
    
    @staticmethod
    def get_image_info_from_bytes(image_bytes: bytes) -> Dict[str, Any]:
        """Get basic image information from bytes"""
        try:
            with Image.open(BytesIO(image_bytes)) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode
                }
        except Exception as e:
            logger.error(f"Error getting image info from bytes: {str(e)}")
            return {}
    
    @staticmethod
    def extract_exif_data_from_bytes(image_bytes: bytes) -> Dict[str, Any]:
        """Extract EXIF data from image bytes"""
        exif_data = {}
        
        try:
            with Image.open(BytesIO(image_bytes)) as img:
                # Get EXIF data if available
                exif = img.getexif()
                
                if exif:
                    # Process standard EXIF tags
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = ImageProcessor._make_json_serializable(value)
                    
                    # Process GPS data
                    if exif.get(34853):  # GPS IFD tag
                        gps_data = {}
                        for tag_id, value in exif.get_ifd(34853).items():
                            tag = GPSTAGS.get(tag_id, tag_id)
                            gps_data[tag] = ImageProcessor._make_json_serializable(value)
                        
                        # Convert GPS coordinates
                        lat, lon, alt = ImageProcessor._convert_gps_coordinates(gps_data)
                        if lat and lon:
                            exif_data['gps_latitude'] = lat
                            exif_data['gps_longitude'] = lon
                            if alt:
                                exif_data['gps_altitude'] = alt
                        
                        exif_data['gps_data'] = gps_data
                
        except Exception as e:
            logger.error(f"Error extracting EXIF data from bytes: {str(e)}")
        
        return exif_data