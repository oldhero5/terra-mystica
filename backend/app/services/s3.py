"""S3 service for handling image storage in AWS S3."""

import io
import logging
from typing import Optional, Tuple, Dict, Any
from datetime import timedelta

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config
from PIL import Image

from app.core.config import settings

logger = logging.getLogger(__name__)


class S3Service:
    """Service for handling S3 operations."""

    def __init__(self):
        """Initialize S3 client with configuration."""
        self.bucket_name = settings.S3_BUCKET_NAME
        self.region = settings.AWS_REGION
        
        # Initialize S3 client with optional endpoint URL for local testing
        self.s3_client = boto3.client(
            "s3",
            region_name=self.region,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.S3_ENDPOINT_URL if settings.S3_ENDPOINT_URL else None,
            config=Config(signature_version="s3v4")
        )

    async def upload_file(
        self, 
        file_content: bytes, 
        key: str, 
        content_type: str = "image/jpeg",
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload a file to S3.
        
        Args:
            file_content: The file content as bytes
            key: The S3 key (path) for the file
            content_type: MIME type of the file
            metadata: Optional metadata to attach to the object
            
        Returns:
            The S3 URL of the uploaded file
        """
        try:
            extra_args = {
                "ContentType": content_type,
                "CacheControl": "max-age=31536000",  # 1 year cache
            }
            
            if metadata:
                extra_args["Metadata"] = metadata
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                **extra_args
            )
            
            # Return the S3 URL
            return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise

    async def upload_image_with_thumbnails(
        self,
        image_content: bytes,
        base_key: str,
        content_type: str = "image/jpeg",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Upload an image and generate thumbnails.
        
        Args:
            image_content: The original image content
            base_key: Base S3 key without extension
            content_type: MIME type of the image
            metadata: Optional metadata
            
        Returns:
            Dictionary with URLs for original and thumbnail versions
        """
        urls = {}
        
        # Upload original image
        original_key = f"{base_key}_original.jpg"
        urls["original"] = await self.upload_file(
            image_content, original_key, content_type, metadata
        )
        
        # Generate and upload thumbnails
        try:
            image = Image.open(io.BytesIO(image_content))
            
            # Convert RGBA to RGB if necessary
            if image.mode in ("RGBA", "LA", "P"):
                rgb_image = Image.new("RGB", image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
                image = rgb_image
            
            # Thumbnail sizes
            sizes = {
                "small": (150, 150),
                "medium": (400, 400),
                "large": (800, 800)
            }
            
            for size_name, dimensions in sizes.items():
                # Create thumbnail
                thumb = image.copy()
                thumb.thumbnail(dimensions, Image.Resampling.LANCZOS)
                
                # Save to bytes
                thumb_io = io.BytesIO()
                thumb.save(thumb_io, format="JPEG", quality=85, optimize=True)
                thumb_io.seek(0)
                
                # Upload thumbnail
                thumb_key = f"{base_key}_{size_name}.jpg"
                urls[size_name] = await self.upload_file(
                    thumb_io.read(),
                    thumb_key,
                    "image/jpeg",
                    metadata
                )
                
        except Exception as e:
            logger.error(f"Error generating thumbnails: {e}")
            # Continue without thumbnails if generation fails
            
        return urls

    def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
        http_method: str = "GET"
    ) -> str:
        """
        Generate a presigned URL for S3 object access.
        
        Args:
            key: The S3 key of the object
            expiration: URL expiration time in seconds
            http_method: HTTP method (GET or PUT)
            
        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod="get_object" if http_method == "GET" else "put_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise

    def generate_presigned_post(
        self,
        key: str,
        expiration: int = 3600,
        max_file_size: int = 10 * 1024 * 1024  # 10MB default
    ) -> Dict[str, Any]:
        """
        Generate presigned POST data for direct browser uploads.
        
        Args:
            key: The S3 key for the upload
            expiration: URL expiration time in seconds
            max_file_size: Maximum file size in bytes
            
        Returns:
            Dictionary with URL and form fields for POST
        """
        try:
            response = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=key,
                ExpiresIn=expiration,
                Conditions=[
                    ["content-length-range", 0, max_file_size],
                    ["starts-with", "$Content-Type", "image/"]
                ]
            )
            return response
        except ClientError as e:
            logger.error(f"Error generating presigned POST: {e}")
            raise

    async def delete_file(self, key: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            key: The S3 key of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            logger.error(f"Error deleting S3 object: {e}")
            return False

    async def delete_image_with_thumbnails(self, base_key: str) -> bool:
        """
        Delete an image and all its thumbnails.
        
        Args:
            base_key: Base S3 key without size suffix
            
        Returns:
            True if all deletions successful
        """
        sizes = ["original", "small", "medium", "large"]
        success = True
        
        for size in sizes:
            key = f"{base_key}_{size}.jpg"
            if not await self.delete_file(key):
                success = False
                
        return success

    def file_exists(self, key: str) -> bool:
        """
        Check if a file exists in S3.
        
        Args:
            key: The S3 key to check
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            logger.error(f"Error checking S3 object existence: {e}")
            raise


# Global S3 service instance
s3_service = S3Service()