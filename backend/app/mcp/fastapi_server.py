"""
MCP Server for FastAPI operations
Provides tools for file system operations, HTTP requests, and system interactions
"""

import os
import json
import aiofiles
import httpx
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

from app.core.config import settings
from app.core.logging import logger

# Initialize MCP server
mcp = FastMCP("Terra Mystica FastAPI Server")


@mcp.tool()
async def read_file(file_path: str) -> str:
    """
    Read contents of a file
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File contents as string
    """
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        logger.info(f"Read file: {file_path}")
        return content
    except Exception as e:
        error_msg = f"Error reading file {file_path}: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool()
async def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file
    
    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        
    Returns:
        Success message or error
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        logger.info(f"Wrote file: {file_path}")
        return f"Successfully wrote {len(content)} characters to {file_path}"
    except Exception as e:
        error_msg = f"Error writing file {file_path}: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool()
async def list_directory(directory_path: str) -> str:
    """
    List contents of a directory
    
    Args:
        directory_path: Path to the directory to list
        
    Returns:
        JSON string of directory contents
    """
    try:
        path = Path(directory_path)
        if not path.exists():
            return f"Directory {directory_path} does not exist"
        
        if not path.is_dir():
            return f"{directory_path} is not a directory"
        
        contents = []
        for item in path.iterdir():
            contents.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None,
                "path": str(item)
            })
        
        logger.info(f"Listed directory: {directory_path}")
        return json.dumps(contents, indent=2)
    except Exception as e:
        error_msg = f"Error listing directory {directory_path}: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool()
async def check_file_exists(file_path: str) -> str:
    """
    Check if a file exists
    
    Args:
        file_path: Path to check
        
    Returns:
        JSON string with existence status and file info
    """
    try:
        path = Path(file_path)
        exists = path.exists()
        
        result = {
            "exists": exists,
            "path": file_path
        }
        
        if exists:
            result.update({
                "is_file": path.is_file(),
                "is_directory": path.is_dir(),
                "size": path.stat().st_size if path.is_file() else None
            })
        
        return json.dumps(result)
    except Exception as e:
        error_msg = f"Error checking file {file_path}: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool()
async def make_http_request(
    method: str, 
    url: str, 
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> str:
    """
    Make HTTP request to FastAPI or external endpoints
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: URL to request
        headers: Optional headers dict
        data: Optional request body data
        timeout: Request timeout in seconds
        
    Returns:
        JSON string with response data
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method.upper(),
                url=url,
                headers=headers or {},
                json=data,
                timeout=timeout
            )
            
            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "url": str(response.url)
            }
            
            # Try to parse JSON response
            try:
                result["json"] = response.json()
            except:
                result["text"] = response.text
            
            logger.info(f"HTTP {method} {url} -> {response.status_code}")
            return json.dumps(result, indent=2)
            
    except Exception as e:
        error_msg = f"Error making HTTP request {method} {url}: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool()
async def get_environment_variable(var_name: str) -> str:
    """
    Get environment variable value
    
    Args:
        var_name: Name of environment variable
        
    Returns:
        Environment variable value or error message
    """
    try:
        value = os.getenv(var_name)
        if value is None:
            return f"Environment variable {var_name} not found"
        
        # Don't log sensitive values
        if any(sensitive in var_name.upper() for sensitive in ['PASSWORD', 'KEY', 'SECRET', 'TOKEN']):
            logger.info(f"Retrieved environment variable: {var_name} (value hidden)")
            return f"Environment variable {var_name} retrieved (value hidden for security)"
        else:
            logger.info(f"Retrieved environment variable: {var_name} = {value}")
            return value
            
    except Exception as e:
        error_msg = f"Error getting environment variable {var_name}: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool()
async def get_upload_directory_info() -> str:
    """
    Get information about upload directories and their contents
    
    Returns:
        JSON string with upload directory structure and stats
    """
    try:
        upload_dir = Path(settings.UPLOAD_DIR)
        thumbnail_dir = Path(settings.THUMBNAIL_DIR)
        
        result = {
            "upload_dir": {
                "path": str(upload_dir),
                "exists": upload_dir.exists(),
                "total_files": 0,
                "total_size": 0,
                "users": []
            },
            "thumbnail_dir": {
                "path": str(thumbnail_dir),
                "exists": thumbnail_dir.exists(),
                "total_files": 0,
                "total_size": 0
            }
        }
        
        # Analyze upload directory
        if upload_dir.exists():
            images_dir = upload_dir / "images"
            if images_dir.exists():
                for user_dir in images_dir.iterdir():
                    if user_dir.is_dir() and user_dir.name.isdigit():
                        user_files = list(user_dir.glob("*"))
                        user_size = sum(f.stat().st_size for f in user_files if f.is_file())
                        
                        result["upload_dir"]["users"].append({
                            "user_id": user_dir.name,
                            "file_count": len(user_files),
                            "total_size": user_size
                        })
                        
                        result["upload_dir"]["total_files"] += len(user_files)
                        result["upload_dir"]["total_size"] += user_size
        
        # Analyze thumbnail directory
        if thumbnail_dir.exists():
            thumb_files = list(thumbnail_dir.glob("*"))
            result["thumbnail_dir"]["total_files"] = len(thumb_files)
            result["thumbnail_dir"]["total_size"] = sum(f.stat().st_size for f in thumb_files if f.is_file())
        
        logger.info("Retrieved upload directory information")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"Error getting upload directory info: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool()
async def create_directory(directory_path: str) -> str:
    """
    Create a directory (including parent directories)
    
    Args:
        directory_path: Path to directory to create
        
    Returns:
        Success message or error
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        logger.info(f"Created directory: {directory_path}")
        return f"Successfully created directory: {directory_path}"
    except Exception as e:
        error_msg = f"Error creating directory {directory_path}: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool()
async def get_image_metadata(image_path: str) -> str:
    """
    Get metadata for an image file
    
    Args:
        image_path: Path to image file
        
    Returns:
        JSON string with image metadata
    """
    try:
        from app.utils.image_processing import ImageProcessor
        
        if not os.path.exists(image_path):
            return f"Image file {image_path} does not exist"
        
        # Get basic image info
        image_info = ImageProcessor.get_image_info(image_path)
        
        # Get EXIF data
        exif_data = ImageProcessor.extract_exif_data(image_path)
        
        result = {
            "file_path": image_path,
            "file_size": os.path.getsize(image_path),
            "basic_info": image_info,
            "exif_data": exif_data
        }
        
        logger.info(f"Retrieved image metadata: {image_path}")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"Error getting image metadata {image_path}: {str(e)}"
        logger.error(error_msg)
        return error_msg


if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport="stdio")