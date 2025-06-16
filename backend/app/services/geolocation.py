"""
Geolocation Service using CrewAI Multi-Agent System
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
from pathlib import Path

from PIL import Image
import structlog

from app.agents.crew import TerraGeolocatorCrew, ImageAnalysisInput, GeoLocationResult
from app.agents.base import AgentConfig
from app.core.config import settings
from app.models.image import ProcessingStatus
from app.schemas.image import ImagePrediction, PredictionLocation


logger = structlog.get_logger()


class GeolocationService:
    """Service for processing images using CrewAI multi-agent system"""
    
    def __init__(self):
        self.crew: Optional[TerraGeolocatorCrew] = None
        self.mcp_client = None  # Will be initialized if MCP is enabled
        self._initialize_crew()
    
    def _initialize_crew(self):
        """Initialize the CrewAI crew with configuration"""
        try:
            # Create agent configuration from settings
            agent_config = AgentConfig()
            
            # Initialize MCP client if configured
            # TODO: Initialize actual MCP client when available
            
            # Create the crew
            self.crew = TerraGeolocatorCrew(
                config=agent_config,
                mcp_client=self.mcp_client,
                verbose=settings.CREWAI_VERBOSE,
            )
            
            logger.info("CrewAI geolocation crew initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize CrewAI crew: {str(e)}")
            raise
    
    async def process_image(
        self,
        image_path: str,
        image_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[callable] = None,
    ) -> ImagePrediction:
        """
        Process an image to predict its geographic location.
        
        Args:
            image_path: Path to the image file
            image_id: Unique identifier for the image
            metadata: Optional metadata including EXIF data
            progress_callback: Optional callback for progress updates
            
        Returns:
            ImagePrediction with location results
        """
        try:
            if progress_callback:
                await progress_callback(0.1, "Starting image analysis...")
            
            # Extract image description
            image_description = await self._extract_image_description(image_path)
            
            if progress_callback:
                await progress_callback(0.2, "Initializing multi-agent analysis...")
            
            # Prepare input for CrewAI
            analysis_input = ImageAnalysisInput(
                image_path=image_path,
                image_description=image_description,
                metadata=metadata or {},
            )
            
            if progress_callback:
                await progress_callback(0.3, "Geographic analysis in progress...")
            
            # Run the multi-agent analysis
            result = await self.crew.analyze_image(analysis_input)
            
            if progress_callback:
                await progress_callback(0.9, "Finalizing predictions...")
            
            # Convert CrewAI result to our schema
            prediction = self._convert_to_prediction(image_id, result)
            
            if progress_callback:
                await progress_callback(1.0, "Analysis complete!")
            
            logger.info(
                "Image processed successfully",
                image_id=image_id,
                primary_location=f"{prediction.latitude},{prediction.longitude}",
                confidence=prediction.confidence,
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error processing image {image_id}: {str(e)}")
            raise
    
    async def _extract_image_description(self, image_path: str) -> str:
        """Extract basic description from image for agent context"""
        try:
            with Image.open(image_path) as img:
                # Basic image properties
                width, height = img.size
                mode = img.mode
                format = img.format
                
                # Extract EXIF data if available
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    # Extract relevant EXIF tags
                    if exif:
                        # GPS data, camera info, datetime, etc.
                        pass
                
                description = f"Image format: {format}, Size: {width}x{height}, Mode: {mode}"
                
                return description
                
        except Exception as e:
            logger.error(f"Error extracting image description: {str(e)}")
            return "Image description unavailable"
    
    def _convert_to_prediction(
        self, image_id: str, result: GeoLocationResult
    ) -> ImagePrediction:
        """Convert CrewAI result to our ImagePrediction schema"""
        primary = result.primary_location
        
        # Create alternative locations
        alternatives = []
        for i, alt in enumerate(result.alternative_locations[:5]):  # Top 5
            alternatives.append(
                PredictionLocation(
                    rank=i + 2,  # Primary is rank 1
                    latitude=alt.latitude,
                    longitude=alt.longitude,
                    confidence=alt.confidence,
                    place_name=alt.place_name,
                    country=alt.country,
                    region=alt.region,
                    reasoning=alt.reasoning,
                )
            )
        
        # Create the prediction
        prediction = ImagePrediction(
            image_id=image_id,
            latitude=primary.latitude,
            longitude=primary.longitude,
            confidence=primary.confidence,
            place_name=primary.place_name or "Unknown",
            country=primary.country or "Unknown",
            region=primary.region,
            reasoning=primary.reasoning,
            alternative_locations=alternatives,
            features=primary.features,
            processing_time=result.processing_time,
            agent_insights=result.agent_insights,
            metadata={
                "model": settings.OPENAI_MODEL,
                "crew_size": 6,
                "mcp_enabled": self.mcp_client is not None,
            },
        )
        
        return prediction
    
    async def validate_prediction(
        self, prediction: ImagePrediction, ground_truth: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Validate a prediction against ground truth if available.
        
        Args:
            prediction: The prediction to validate
            ground_truth: Optional dict with 'latitude' and 'longitude'
            
        Returns:
            Validation results including accuracy metrics
        """
        validation = {
            "prediction_id": prediction.image_id,
            "confidence": prediction.confidence,
            "agent_consensus": len(prediction.agent_insights),
        }
        
        if ground_truth:
            # Calculate distance between prediction and ground truth
            from math import radians, cos, sin, asin, sqrt
            
            def haversine(lon1, lat1, lon2, lat2):
                """Calculate the great circle distance between two points"""
                lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                r = 6371  # Radius of earth in kilometers
                return c * r * 1000  # Convert to meters
            
            distance = haversine(
                prediction.longitude,
                prediction.latitude,
                ground_truth["longitude"],
                ground_truth["latitude"],
            )
            
            validation.update({
                "distance_meters": distance,
                "within_50m": distance <= 50,
                "within_100m": distance <= 100,
                "within_500m": distance <= 500,
                "within_1km": distance <= 1000,
            })
            
            logger.info(
                "Prediction validated",
                prediction_id=prediction.image_id,
                distance_meters=distance,
                within_50m=validation["within_50m"],
            )
        
        return validation
    
    def get_crew_status(self) -> Dict[str, Any]:
        """Get the status of the CrewAI crew"""
        if not self.crew:
            return {"status": "not_initialized"}
        
        return {
            "status": "active",
            "agents": self.crew.get_agent_statuses(),
            "config": {
                "model": settings.OPENAI_MODEL,
                "temperature": settings.OPENAI_TEMPERATURE,
                "max_iterations": settings.CREWAI_MAX_ITERATIONS,
            },
            "mcp_enabled": self.mcp_client is not None,
        }


# Global service instance
geolocation_service = GeolocationService()