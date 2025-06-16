"""
Geolocation API endpoints
"""

from typing import Optional, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.image import Image, ProcessingStatus
from app.schemas.image import ImagePrediction
from app.services.geolocation import geolocation_service
from app.services.s3 import s3_service
from app.core.logging import logger
from app.api.websocket import manager, create_progress_callback


router = APIRouter()


@router.post("/predict/{image_id}", response_model=ImagePrediction)
async def predict_location(
    image_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ImagePrediction:
    """
    Process an image to predict its geographic location using CrewAI multi-agent system.
    
    This endpoint triggers the geolocation analysis for a previously uploaded image.
    """
    # Get the image from database
    image = await db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Check if user owns the image
    if image.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this image")
    
    # Check if already processed
    if image.status == ProcessingStatus.COMPLETED:
        if image.prediction_data:
            return ImagePrediction(**image.prediction_data)
        else:
            raise HTTPException(
                status_code=400,
                detail="Image already processed but prediction data is missing"
            )
    
    # Check if processing is in progress
    if image.status == ProcessingStatus.PROCESSING:
        raise HTTPException(
            status_code=400,
            detail="Image is already being processed"
        )
    
    # Update status to processing
    image.status = ProcessingStatus.PROCESSING
    await db.commit()
    
    # Process the image in background
    background_tasks.add_task(
        process_image_background,
        image_id=image_id,
        s3_key=image.s3_key,
        metadata=image.metadata,
        user_id=current_user.id,
    )
    
    return JSONResponse(
        content={
            "message": "Processing started",
            "image_id": image_id,
            "status": "processing"
        },
        status_code=202
    )


async def process_image_background(
    image_id: str,
    s3_key: str,
    metadata: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
):
    """Background task to process image"""
    from app.core.deps import get_db_context
    
    try:
        # Create progress callback for WebSocket updates
        progress_callback = create_progress_callback(user_id, image_id) if user_id else None
        
        # Download image from S3
        local_path = f"/tmp/{image_id}.jpg"
        await s3_service.download_file(s3_key, local_path)
        
        # Process with CrewAI
        prediction = await geolocation_service.process_image(
            image_path=local_path,
            image_id=image_id,
            metadata=metadata,
            progress_callback=progress_callback,
        )
        
        # Update database with results
        async with get_db_context() as db:
            image = await db.get(Image, image_id)
            if image:
                image.status = ProcessingStatus.COMPLETED
                image.prediction_data = prediction.model_dump()
                image.latitude = prediction.latitude
                image.longitude = prediction.longitude
                image.confidence = prediction.confidence
                await db.commit()
        
        # Send completion notification via WebSocket
        if user_id:
            await manager.send_completion(
                user_id=user_id,
                image_id=image_id,
                success=True,
                result={
                    "latitude": prediction.latitude,
                    "longitude": prediction.longitude,
                    "confidence": prediction.confidence,
                    "place_name": prediction.place_name,
                }
            )
        
        # Clean up temp file
        import os
        if os.path.exists(local_path):
            os.remove(local_path)
            
    except Exception as e:
        logger.error(f"Error processing image {image_id}: {str(e)}")
        
        # Update status to failed
        async with get_db_context() as db:
            image = await db.get(Image, image_id)
            if image:
                image.status = ProcessingStatus.FAILED
                image.error_message = str(e)
                await db.commit()
        
        # Send failure notification via WebSocket
        if user_id:
            await manager.send_completion(
                user_id=user_id,
                image_id=image_id,
                success=False,
                error=str(e),
            )


@router.get("/results/{image_id}", response_model=ImagePrediction)
async def get_prediction_results(
    image_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ImagePrediction:
    """Get the geolocation prediction results for an image."""
    # Get the image from database
    image = await db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Check if user owns the image
    if image.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this image")
    
    # Check processing status
    if image.status == ProcessingStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Image has not been processed yet"
        )
    elif image.status == ProcessingStatus.PROCESSING:
        raise HTTPException(
            status_code=202,
            detail="Image is still being processed"
        )
    elif image.status == ProcessingStatus.FAILED:
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {image.error_message}"
        )
    
    # Return prediction data
    if image.prediction_data:
        return ImagePrediction(**image.prediction_data)
    else:
        raise HTTPException(
            status_code=500,
            detail="Prediction data is missing"
        )


@router.get("/crew/status")
async def get_crew_status(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get the status of the CrewAI multi-agent crew."""
    return geolocation_service.get_crew_status()


@router.post("/validate/{image_id}")
async def validate_prediction(
    image_id: str,
    ground_truth: Dict[str, float],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Validate a prediction against ground truth coordinates.
    
    Args:
        image_id: The image ID
        ground_truth: Dict with 'latitude' and 'longitude' keys
    
    Returns:
        Validation metrics including distance and accuracy
    """
    # Validate ground truth format
    if "latitude" not in ground_truth or "longitude" not in ground_truth:
        raise HTTPException(
            status_code=400,
            detail="Ground truth must include 'latitude' and 'longitude'"
        )
    
    # Get the image and prediction
    image = await db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    if image.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if image.status != ProcessingStatus.COMPLETED or not image.prediction_data:
        raise HTTPException(
            status_code=400,
            detail="Image must be processed before validation"
        )
    
    # Validate the prediction
    prediction = ImagePrediction(**image.prediction_data)
    validation_result = await geolocation_service.validate_prediction(
        prediction, ground_truth
    )
    
    # Store validation result in image metadata
    if not image.metadata:
        image.metadata = {}
    image.metadata["validation"] = validation_result
    await db.commit()
    
    return validation_result