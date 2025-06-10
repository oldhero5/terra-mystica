"""
MCP Server for PostgreSQL operations
Provides tools for database queries, user management, and data analysis
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.logging import logger
from app.models.user import User
from app.models.image import Image, ImageProcessingTask

# Initialize MCP server
mcp = FastMCP("Terra Mystica PostgreSQL Server")

# Create async engine and session
engine = create_async_engine(settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"))
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@mcp.tool()
async def execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> str:
    """
    Execute a SQL query and return results
    
    Args:
        query: SQL query to execute
        params: Optional parameters for the query
        
    Returns:
        JSON string with query results
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text(query), params or {})
            
            if result.returns_rows:
                rows = result.fetchall()
                columns = result.keys()
                
                data = []
                for row in rows:
                    data.append(dict(zip(columns, row)))
                
                response = {
                    "success": True,
                    "row_count": len(data),
                    "columns": list(columns),
                    "data": data
                }
            else:
                response = {
                    "success": True,
                    "rows_affected": result.rowcount,
                    "data": None
                }
            
            await session.commit()
            
        logger.info(f"Executed query: {query[:100]}...")
        return json.dumps(response, indent=2, default=str)
        
    except Exception as e:
        error_msg = f"Error executing query: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"success": False, "error": error_msg})


@mcp.tool()
async def get_user_info(user_id: int) -> str:
    """
    Get detailed information about a user
    
    Args:
        user_id: ID of the user
        
    Returns:
        JSON string with user information and statistics
    """
    try:
        async with AsyncSessionLocal() as session:
            # Get user
            user_query = text("SELECT * FROM users WHERE id = :user_id")
            user_result = await session.execute(user_query, {"user_id": user_id})
            user_row = user_result.fetchone()
            
            if not user_row:
                return json.dumps({"success": False, "error": f"User {user_id} not found"})
            
            user_data = dict(zip(user_result.keys(), user_row))
            
            # Get user's image statistics
            stats_query = text("""
                SELECT 
                    COUNT(*) as total_images,
                    COUNT(CASE WHEN status = 'uploaded' THEN 1 END) as uploaded_count,
                    COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_count,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count,
                    SUM(file_size) as total_file_size,
                    COUNT(CASE WHEN predicted_latitude IS NOT NULL THEN 1 END) as geolocated_count
                FROM images 
                WHERE user_id = :user_id AND is_deleted = false
            """)
            stats_result = await session.execute(stats_query, {"user_id": user_id})
            stats_row = stats_result.fetchone()
            stats_data = dict(zip(stats_result.keys(), stats_row))
            
            result = {
                "success": True,
                "user": user_data,
                "statistics": stats_data
            }
            
        logger.info(f"Retrieved user info for user_id: {user_id}")
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        error_msg = f"Error getting user info: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"success": False, "error": error_msg})


@mcp.tool()
async def get_image_info(image_id: int) -> str:
    """
    Get detailed information about an image
    
    Args:
        image_id: ID of the image
        
    Returns:
        JSON string with image information and processing status
    """
    try:
        async with AsyncSessionLocal() as session:
            # Get image with user info
            image_query = text("""
                SELECT 
                    i.*,
                    u.username,
                    u.email
                FROM images i
                JOIN users u ON i.user_id = u.id
                WHERE i.id = :image_id
            """)
            image_result = await session.execute(image_query, {"image_id": image_id})
            image_row = image_result.fetchone()
            
            if not image_row:
                return json.dumps({"success": False, "error": f"Image {image_id} not found"})
            
            image_data = dict(zip(image_result.keys(), image_row))
            
            # Get processing tasks for this image
            tasks_query = text("""
                SELECT * FROM image_processing_tasks 
                WHERE image_id = :image_id 
                ORDER BY created_at DESC
            """)
            tasks_result = await session.execute(tasks_query, {"image_id": image_id})
            tasks_rows = tasks_result.fetchall()
            
            tasks_data = []
            for row in tasks_rows:
                tasks_data.append(dict(zip(tasks_result.keys(), row)))
            
            result = {
                "success": True,
                "image": image_data,
                "processing_tasks": tasks_data
            }
            
        logger.info(f"Retrieved image info for image_id: {image_id}")
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        error_msg = f"Error getting image info: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"success": False, "error": error_msg})


@mcp.tool()
async def update_image_status(image_id: int, status: str, error_message: Optional[str] = None) -> str:
    """
    Update image processing status
    
    Args:
        image_id: ID of the image
        status: New status (uploaded, processing, completed, failed)
        error_message: Optional error message if status is failed
        
    Returns:
        JSON string with update result
    """
    try:
        async with AsyncSessionLocal() as session:
            update_query = text("""
                UPDATE images 
                SET status = :status, 
                    error_message = :error_message,
                    processing_started_at = CASE 
                        WHEN :status = 'processing' AND processing_started_at IS NULL 
                        THEN NOW() 
                        ELSE processing_started_at 
                    END,
                    processing_completed_at = CASE 
                        WHEN :status IN ('completed', 'failed') 
                        THEN NOW() 
                        ELSE processing_completed_at 
                    END,
                    updated_at = NOW()
                WHERE id = :image_id
            """)
            
            result = await session.execute(update_query, {
                "image_id": image_id,
                "status": status,
                "error_message": error_message
            })
            
            await session.commit()
            
            response = {
                "success": True,
                "image_id": image_id,
                "status": status,
                "rows_affected": result.rowcount
            }
            
        logger.info(f"Updated image {image_id} status to {status}")
        return json.dumps(response)
        
    except Exception as e:
        error_msg = f"Error updating image status: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"success": False, "error": error_msg})


@mcp.tool()
async def save_geolocation_result(
    image_id: int,
    latitude: float,
    longitude: float,
    confidence_score: float,
    alternative_locations: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Save geolocation prediction results for an image
    
    Args:
        image_id: ID of the image
        latitude: Predicted latitude
        longitude: Predicted longitude
        confidence_score: Confidence score (0.0 to 1.0)
        alternative_locations: List of alternative location predictions
        
    Returns:
        JSON string with save result
    """
    try:
        async with AsyncSessionLocal() as session:
            update_query = text("""
                UPDATE images 
                SET predicted_latitude = :latitude,
                    predicted_longitude = :longitude,
                    confidence_score = :confidence_score,
                    alternative_locations = :alternative_locations,
                    status = 'completed',
                    processing_completed_at = NOW(),
                    updated_at = NOW()
                WHERE id = :image_id
            """)
            
            result = await session.execute(update_query, {
                "image_id": image_id,
                "latitude": latitude,
                "longitude": longitude,
                "confidence_score": confidence_score,
                "alternative_locations": json.dumps(alternative_locations) if alternative_locations else None
            })
            
            await session.commit()
            
            response = {
                "success": True,
                "image_id": image_id,
                "latitude": latitude,
                "longitude": longitude,
                "confidence_score": confidence_score,
                "rows_affected": result.rowcount
            }
            
        logger.info(f"Saved geolocation result for image {image_id}: ({latitude}, {longitude})")
        return json.dumps(response)
        
    except Exception as e:
        error_msg = f"Error saving geolocation result: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"success": False, "error": error_msg})


@mcp.tool()
async def create_processing_task(
    image_id: int,
    task_type: str,
    task_id: Optional[str] = None
) -> str:
    """
    Create a new processing task for an image
    
    Args:
        image_id: ID of the image
        task_type: Type of task (thumbnail, geolocation, etc.)
        task_id: Optional external task ID (e.g., Celery task ID)
        
    Returns:
        JSON string with created task info
    """
    try:
        async with AsyncSessionLocal() as session:
            insert_query = text("""
                INSERT INTO image_processing_tasks 
                (image_id, task_type, task_id, status, progress, created_at)
                VALUES (:image_id, :task_type, :task_id, 'pending', 0, NOW())
                RETURNING id
            """)
            
            result = await session.execute(insert_query, {
                "image_id": image_id,
                "task_type": task_type,
                "task_id": task_id
            })
            
            task_db_id = result.scalar()
            await session.commit()
            
            response = {
                "success": True,
                "task_id": task_db_id,
                "image_id": image_id,
                "task_type": task_type,
                "external_task_id": task_id
            }
            
        logger.info(f"Created processing task {task_db_id} for image {image_id}")
        return json.dumps(response)
        
    except Exception as e:
        error_msg = f"Error creating processing task: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"success": False, "error": error_msg})


@mcp.tool()
async def update_task_progress(task_id: int, progress: int, current_step: Optional[str] = None) -> str:
    """
    Update progress of a processing task
    
    Args:
        task_id: ID of the processing task
        progress: Progress percentage (0-100)
        current_step: Optional description of current step
        
    Returns:
        JSON string with update result
    """
    try:
        async with AsyncSessionLocal() as session:
            update_query = text("""
                UPDATE image_processing_tasks 
                SET progress = :progress,
                    current_step = :current_step,
                    status = CASE 
                        WHEN :progress = 100 THEN 'completed'
                        WHEN :progress > 0 THEN 'processing'
                        ELSE status 
                    END,
                    started_at = CASE 
                        WHEN :progress > 0 AND started_at IS NULL 
                        THEN NOW() 
                        ELSE started_at 
                    END,
                    completed_at = CASE 
                        WHEN :progress = 100 
                        THEN NOW() 
                        ELSE completed_at 
                    END
                WHERE id = :task_id
            """)
            
            result = await session.execute(update_query, {
                "task_id": task_id,
                "progress": progress,
                "current_step": current_step
            })
            
            await session.commit()
            
            response = {
                "success": True,
                "task_id": task_id,
                "progress": progress,
                "current_step": current_step,
                "rows_affected": result.rowcount
            }
            
        logger.info(f"Updated task {task_id} progress to {progress}%")
        return json.dumps(response)
        
    except Exception as e:
        error_msg = f"Error updating task progress: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"success": False, "error": error_msg})


@mcp.tool()
async def get_pending_images() -> str:
    """
    Get all images that need geolocation processing
    
    Returns:
        JSON string with pending images
    """
    try:
        async with AsyncSessionLocal() as session:
            query = text("""
                SELECT 
                    i.id,
                    i.user_id,
                    i.filename,
                    i.original_filename,
                    i.file_path,
                    i.status,
                    i.exif_latitude,
                    i.exif_longitude,
                    i.created_at,
                    u.username,
                    u.email
                FROM images i
                JOIN users u ON i.user_id = u.id
                WHERE i.status IN ('uploaded', 'processing') 
                AND i.is_deleted = false
                AND i.predicted_latitude IS NULL
                ORDER BY i.created_at ASC
            """)
            
            result = await session.execute(query)
            rows = result.fetchall()
            
            data = []
            for row in rows:
                data.append(dict(zip(result.keys(), row)))
            
            response = {
                "success": True,
                "count": len(data),
                "pending_images": data
            }
            
        logger.info(f"Retrieved {len(data)} pending images")
        return json.dumps(response, indent=2, default=str)
        
    except Exception as e:
        error_msg = f"Error getting pending images: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"success": False, "error": error_msg})


@mcp.tool()
async def get_database_stats() -> str:
    """
    Get overall database statistics
    
    Returns:
        JSON string with database statistics
    """
    try:
        async with AsyncSessionLocal() as session:
            stats_query = text("""
                SELECT 
                    (SELECT COUNT(*) FROM users) as total_users,
                    (SELECT COUNT(*) FROM images WHERE is_deleted = false) as total_images,
                    (SELECT COUNT(*) FROM images WHERE status = 'completed' AND is_deleted = false) as completed_images,
                    (SELECT COUNT(*) FROM images WHERE status = 'processing' AND is_deleted = false) as processing_images,
                    (SELECT COUNT(*) FROM images WHERE status = 'failed' AND is_deleted = false) as failed_images,
                    (SELECT COUNT(*) FROM image_processing_tasks) as total_tasks,
                    (SELECT SUM(file_size) FROM images WHERE is_deleted = false) as total_storage_bytes,
                    (SELECT COUNT(*) FROM images WHERE predicted_latitude IS NOT NULL AND is_deleted = false) as geolocated_images
            """)
            
            result = await session.execute(stats_query)
            row = result.fetchone()
            stats_data = dict(zip(result.keys(), row))
            
            response = {
                "success": True,
                "statistics": stats_data
            }
            
        logger.info("Retrieved database statistics")
        return json.dumps(response, indent=2, default=str)
        
    except Exception as e:
        error_msg = f"Error getting database stats: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"success": False, "error": error_msg})


if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport="stdio")